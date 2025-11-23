from utils import gen_successors


def iddfs(start, goal, R, C, order_spec=None, max_depth=50, max_nodes=None):
    nodes = 0
    def dls(state, depth, path, visited_set):
        nonlocal nodes
        nodes += 1
        if max_nodes and nodes > max_nodes:
            return None, True
        if state == goal:
            return path, True
        if depth == 0:
            return None, False
        cutoff = False
        for m, ns in gen_successors(state, R, C, order_spec):
            if ns in visited_set:
                continue
            visited_set.add(ns)
            res, finished = dls(ns, depth-1, path + m, visited_set)
            visited_set.remove(ns)
            if finished:
                return res, True
            if res is None:
                cutoff = True
        return None, False if not cutoff else (None, False)


    for depth in range(max_depth+1):
        res, finished = dls(start, depth, "", {start})
        if res is not None:
            return res
    return None