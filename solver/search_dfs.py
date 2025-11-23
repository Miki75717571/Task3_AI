from utils import gen_successors


def dfs(start, goal, R, C, order_spec=None, max_nodes=None):
    nodes = 0
    stack = [(start, "")]
    visited_global = set()
    while stack:
        state, path = stack.pop()
        nodes += 1
        if max_nodes and nodes > max_nodes:
            return None
        if state == goal:
            return path
        succs = gen_successors(state, R, C, order_spec)
        for m, ns in reversed(succs):
            if ns in visited_global:
                continue
            stack.append((ns, path + m))
        visited_global.add(state)
    return None