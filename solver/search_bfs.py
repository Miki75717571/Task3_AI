from collections import deque
from utils import gen_successors


def bfs(start, goal, R, C, order_spec=None, max_nodes=None):
    if start == goal:
        return ''
    q = deque()
    q.append((start, ""))
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