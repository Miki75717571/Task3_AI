# Uwaga: SMA* jest rozbudowanym algorytmem; poniżej szkic implementacji
# zamiast pełnej, bezpiecznej implementacji produkcyjnej. Służy do porównań
# w ćwiczeniach — ograniczamy liczbę przechowywanych węzłów (max_memory).


import heapq
from utils import gen_successors


class Node:
    def __init__(self, state, path, g, f):
        self.state = state
        self.path = path
        self.g = g
        self.f = f
    def __lt__(self, other):
        return self.f < other.f


def sma_star(start, goal, R, C, heur_fn, goal_pos, order_spec=None, max_nodes=None, max_memory=10000):
# bardzo uproszczona wersja: działanie podobne do A* z ograniczeniem rozmiaru open-listy
    open_heap = []
    f0 = heur_fn(start, R, C, goal_pos)
    heapq.heappush(open_heap, (f0, 0, start, "", 0))
    nodes = 0
    tie = 0
    visited = set()
    while open_heap:
        f, _, state, path, g = heapq.heappop(open_heap)
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
            ng = g + 1
            nf = ng + heur_fn(ns, R, C, goal_pos)
            tie += 1
            heapq.heappush(open_heap, (nf, tie, ns, path + m, ng))
# memory control
        if len(open_heap) > max_memory:
# usuń element o największym f (najgorszy)
            open_heap.sort(key=lambda x: (-x[0], x[1]))
            open_heap.pop(0)
    return None