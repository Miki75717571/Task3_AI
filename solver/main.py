#!/usr/bin/env python3
import sys
import argparse
from collections import deque
import heapq
import random
import time

# ---------- utility: state representation ----------
# Representujemy stan jako 1D tuple długości R*C, gdzie 0 = pusta
# indeksy: row * C + col

def read_input():
    R, C = 4, 4         
    data = sys.stdin.read().strip().split()

    if not data:
        print("No input", file=sys.stderr)
        sys.exit(1)

    # oczekujemy 16 wartości
    if len(data) != 16:
        print(f"Error: expected 16 numbers, got {len(data)}", file=sys.stderr)
        sys.exit(1)

    arr = list(map(int, data))
    return R, C, tuple(arr)


def idx_to_rc(idx, C):
    return divmod(idx, C)

def rc_to_idx(r, c, C):
    return r * C + c

def goal_state(R, C):
    # last cell is 0
    vals = list(range(1, R*C))
    vals.append(0)
    return tuple(vals)

# ---------- moves generation ----------
MOVES = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1)
}

def gen_successors(state, R, C, order_spec):
    """Zwraca listę (move_char, new_state) zgodnie z order_spec.
       Jeśli order_spec zaczyna się od 'R' => randomizujemy kolejność dla każdego węzła.
    """
    zero_idx = state.index(0)
    zr, zc = idx_to_rc(zero_idx, C)
    # compute order
    if order_spec and order_spec[0] == 'R':
        order = ['L','R','U','D']
        random.shuffle(order)
    else:
        if order_spec:
            order = list(order_spec)
        else:
            order = ['L','R','U','D']
    succ = []
    for m in order:
        dr, dc = MOVES[m]
        nr, nc = zr + dr, zc + dc
        if 0 <= nr < R and 0 <= nc < C:
            nidx = rc_to_idx(nr, nc, C)
            lst = list(state)
            # swap zero with target tile (we move tile into zero => char means tile move)
            lst[zero_idx], lst[nidx] = lst[nidx], lst[zero_idx]
            succ.append((m, tuple(lst)))
    return succ

# ---------- solvability check (generalized for R*C) ----------
# For 15-puzzle (4x4): state solvable iff (inversion_count + row_of_blank_from_bottom) % 2 == target parity
def inversion_count(state, R, C):
    arr = [x for x in state if x != 0]
    inv = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1
    return inv

def is_solvable(state, R, C, goal=None):
    inv = inversion_count(state, R, C)
    if C % 2 == 1:
        # odd width: solvable iff inversions parity equals goal parity
        if goal is None:
            return inv % 2 == 0
        else:
            return (inv % 2) == (inversion_count(goal, R, C) % 2)
    else:
        # even width: blank row from bottom matters
        zr, zc = idx_to_rc(state.index(0), C)
        blank_row_from_bottom = R - zr
        if goal is None:
            return (inv + blank_row_from_bottom) % 2 == 0
        else:
            g_inv = inversion_count(goal, R, C)
            gr, gc = idx_to_rc(goal.index(0), C)
            g_blank_row_from_bottom = R - gr
            return ((inv + blank_row_from_bottom) % 2) == ((g_inv + g_blank_row_from_bottom) % 2)

# ---------- heuristics ----------
def h_zero(state, R, C, goal_pos):
    return 0

def h_misplaced(state, R, C, goal_pos):
    count = 0
    for idx, val in enumerate(state):
        if val != 0:
            goal_idx = goal_pos[val]
            if goal_idx != idx:
                count += 1
    return count

def h_manhattan(state, R, C, goal_pos):
    s = 0
    for idx, val in enumerate(state):
        if val != 0:
            gr, gc = idx_to_rc(goal_pos[val], C)
            r, c = idx_to_rc(idx, C)
            s += abs(r - gr) + abs(c - gc)
    return s

# prepare goal pos map: val -> index
def make_goal_pos_map(goal):
    pos = {}
    for idx, val in enumerate(goal):
        if val != 0:
            pos[val] = idx
    return pos

# ---------- search algorithms ----------
def bfs(start, goal, R, C, order_spec=None, max_nodes=None):
    if start == goal:
        return []
    q = deque()
    q.append((start, ""))  # state, path
    visited = {start}
    nodes = 0
    while q:
        state, path = q.popleft()
        nodes += 1
        if max_nodes and nodes > max_nodes:
            return None
        for m, ns in gen_successors(state, R, C, order_spec):
            if ns in visited:
                continue
            if ns == goal:
                return path + m
            visited.add(ns)
            q.append((ns, path + m))
    return None

def dfs(start, goal, R, C, order_spec=None, max_nodes=None):
    # Depth-first with visited-per-path (to avoid cycles). Non-iterative limitless DFS.
    nodes = 0
    visited_global = set()
    stack = [(start, "")]  # iterative stack (LIFO)
    while stack:
        state, path = stack.pop()
        nodes += 1
        if max_nodes and nodes > max_nodes:
            return None
        if state == goal:
            return path
        # We will not mark globally visited here to allow deeper paths, but to avoid infinite loops
        # we can use path-set
        path_set = set()
        # generate successors in reverse order for stack LIFO so the first in order is popped first
        succs = gen_successors(state, R, C, order_spec)
        # push in reverse so first order is explored first
        for m, ns in reversed(succs):
            # avoid immediate cycle with parent by checking last move inverted
            # better: check if ns appears in path by reconstructing states from path (costly)
            # approximate: maintain global visited to prune repeated states
            if ns in visited_global:
                continue
            stack.append((ns, path + m))
        visited_global.add(state)
    return None

def iddfs(start, goal, R, C, order_spec=None, max_depth=50, max_nodes=None):
    # iterative deepening DFS
    def dls(state, goal, depth, path, visited_set):
        nonlocal nodes
        nodes += 1
        if max_nodes and nodes > max_nodes:
            return None, True
        if state == goal:
            return path, True
        if depth == 0:
            return None, False
        cutoff_occurred = False
        for m, ns in gen_successors(state, R, C, order_spec):
            if ns in visited_set:
                continue
            visited_set.add(ns)
            res, finished = dls(ns, goal, depth-1, path + m, visited_set)
            visited_set.remove(ns)
            if finished:
                return res, True
            if res is None:
                cutoff_occurred = True
        return None, False if not cutoff_occurred else (None, False)
    nodes = 0
    for depth in range(max_depth+1):
        visited = {start}
        res, finished = dls(start, goal, depth, "", visited)
        if res is not None:
            return res
    return None

def best_first(start, goal, R, C, heur_fn, goal_pos, order_spec=None, max_nodes=None):
    if start == goal:
        return []
    nodes = 0
    heap = []
    # priority by h only
    h0 = heur_fn(start, R, C, goal_pos)
    heapq.heappush(heap, (h0, 0, start, ""))  # (priority, tie-breaker, state, path)
    visited = set()
    tie = 0
    while heap:
        hval, _, state, path = heapq.heappop(heap)
        nodes += 1
        if max_nodes and nodes > max_nodes:
            return None
        if state == goal:
            return path
        if state in visited:
            continue
        visited.add(state)
        for m, ns in gen_successors(state, R, C, order_spec):
            if ns in visited:
                continue
            tie += 1
            hv = heur_fn(ns, R, C, goal_pos)
            heapq.heappush(heap, (hv, tie, ns, path + m))
    return None

def astar(start, goal, R, C, heur_fn, goal_pos, order_spec=None, max_nodes=None):
    if start == goal:
        return []
    nodes = 0
    open_heap = []
    g_scores = {start: 0}
    f0 = heur_fn(start, R, C, goal_pos)
    heapq.heappush(open_heap, (f0, 0, start, ""))  # (f, tie, state, path)
    closed = {}
    tie = 0
    while open_heap:
        f, _, state, path = heapq.heappop(open_heap)
        nodes += 1
        if max_nodes and nodes > max_nodes:
            return None
        if state == goal:
            return path
        g = g_scores.get(state, float('inf'))
        # If we've seen a better g before, skip
        if state in closed and closed[state] <= g:
            continue
        closed[state] = g
        for m, ns in gen_successors(state, R, C, order_spec):
            tentative_g = g + 1
            if ns in closed and tentative_g >= closed.get(ns, float('inf')):
                continue
            if tentative_g < g_scores.get(ns, float('inf')):
                g_scores[ns] = tentative_g
                tie += 1
                fscore = tentative_g + heur_fn(ns, R, C, goal_pos)
                heapq.heappush(open_heap, (fscore, tie, ns, path + m))
    return None

# ---------- main CLI and dispatch ----------
def main():
    parser = argparse.ArgumentParser(description="15-puzzle solver (supports BFS, DFS, IDDFS, Best-first, A*)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b','--bfs', metavar='ORDER', help="Breadth-first search order (e.g. DULR or R... for random)")
    group.add_argument('-d','--dfs', metavar='ORDER', help="Depth-first search order")
    group.add_argument('-i','--idfs', metavar='ORDER', help="Iterative deepening DFS order")
    group.add_argument('-he','--bf', metavar='HEUR', help="Best-first using heuristic (manhattan|misplaced|zero)")
    group.add_argument('-a','--astar', metavar='HEUR', help="A* using heuristic (manhattan|misplaced|zero)")
    parser.add_argument('--max_nodes', type=int, default=1000000, help="Optional limit on number of expanded nodes")
    parser.add_argument('--max_depth', type=int, default=50, help="Max depth for IDDFS")
    args = parser.parse_args()

    R, C, start = read_input()
    goal = goal_state(R, C)
    if not is_solvable(start, R, C, goal):
        # print output format: -1 and empty second line
        print(-1)
        print("")
        return

    # heuristics map
    goal_pos = make_goal_pos_map(goal)
    heur_map = {
        'manhattan': lambda s, R_, C_, gp: h_manhattan(s, R_, C_, gp),
        'misplaced': lambda s, R_, C_, gp: h_misplaced(s, R_, C_, gp),
        'zero': lambda s, R_, C_, gp: h_zero(s, R_, C_, gp)
    }

    # dispatch based on args
    start_time = time.time()
    solution = None
    if args.bfs is not None:
        order = args.bfs
        solution = bfs(start, goal, R, C, order_spec=order, max_nodes=args.max_nodes)
    elif args.dfs is not None:
        order = args.dfs
        solution = dfs(start, goal, R, C, order_spec=order, max_nodes=args.max_nodes)
    elif args.idfs is not None:
        order = args.idfs
        solution = iddfs(start, goal, R, C, order_spec=order, max_depth=args.max_depth, max_nodes=args.max_nodes)
    elif args.bf is not None:
        heur = args.bf
        if heur not in heur_map:
            print("Unknown heuristic", file=sys.stderr); sys.exit(1)
        solution = best_first(start, goal, R, C, heur_map[heur], goal_pos, order_spec=None, max_nodes=args.max_nodes)
    elif args.astar is not None:
        heur = args.astar
        if heur not in heur_map:
            print("Unknown heuristic", file=sys.stderr); sys.exit(1)
        solution = astar(start, goal, R, C, heur_map[heur], goal_pos, order_spec=None, max_nodes=args.max_nodes)
    end_time = time.time()

    if solution is None:
        print(-1)
        print("")
    else:
        print(len(solution))
        print(solution)
    # optional diagnostic
    # print(f"# time: {end_time - start_time:.3f}s", file=sys.stderr)

if __name__ == "__main__":
    main()
