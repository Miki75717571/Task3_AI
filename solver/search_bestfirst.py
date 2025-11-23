import heapq
from utils import gen_successors


def best_first(start, goal, R, C, heur_fn, goal_pos, order_spec=None, max_nodes=None):
    if start == goal:
        return ''
    heap = []
    h0 = heur_fn(start, R, C, goal_pos)
    heapq.heappush(heap, (h0, 0, start, ""))
    visited = set()
    tie = 0
    nodes = 0
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