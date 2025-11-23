import heapq
from utils import gen_successors


def astar(start, goal, R, C, heur_fn, goal_pos, order_spec=None, max_nodes=None):
    if start == goal:
        return ''
    open_heap = []
    g_scores = {start: 0}
    f0 = heur_fn(start, R, C, goal_pos)
    heapq.heappush(open_heap, (f0, 0, start, ""))
    closed = {}
    tie = 0
    nodes = 0
    while open_heap:
        f, _, state, path = heapq.heappop(open_heap)
        nodes += 1
        if max_nodes and nodes > max_nodes:
            return None
        if state == goal:
            return path
        g = g_scores.get(state, float('inf'))
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