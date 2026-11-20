"""Kruskal's algorithm: sort edges, add cheapest edge that does not form a cycle.
Time: O(E log E) (sorting) + O(E a(V)) (union-find)."""
import time

from .dsu import DisjointSet
from .graph import Graph, MSTResult


def kruskal_mst(graph: Graph) -> MSTResult:
    t0 = time.perf_counter()
    dsu = DisjointSet(graph.n)
    chosen = []
    total = 0.0
    for u, v, w in sorted(graph.edges, key=lambda e: e[2]):
        if dsu.union(u, v):
            chosen.append((u, v, w))
            total += w
            if dsu.components == 1:              # early exit: tree complete
                break
    ms = (time.perf_counter() - t0) * 1000
    return MSTResult("Kruskal", chosen, total, dsu.components <= 1, ms)
