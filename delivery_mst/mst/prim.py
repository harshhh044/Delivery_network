"""Prim's algorithm: grow a tree from a start vertex, always adding the cheapest
edge leaving the tree.
  prim_mst        : binary heap + adjacency list, O(E log V)  (good for sparse graphs)
  prim_mst_dense  : array scan + adjacency matrix, O(V^2)     (good for dense graphs)
Both return a minimum spanning forest if the graph is disconnected."""
import heapq
import time

from .graph import Graph, MSTResult


def prim_mst(graph: Graph) -> MSTResult:
    t0 = time.perf_counter()
    n = graph.n
    adj = graph.adj
    visited = [False] * n
    chosen, total, comps = [], 0.0, 0
    for start in range(n):                       # loop handles disconnected graphs
        if visited[start]:
            continue
        comps += 1
        visited[start] = True
        heap = [(w, start, v) for v, w in adj[start]]
        heapq.heapify(heap)
        while heap:
            w, u, v = heapq.heappop(heap)
            if visited[v]:
                continue
            visited[v] = True
            chosen.append((u, v, w))
            total += w
            for x, wx in adj[v]:
                if not visited[x]:
                    heapq.heappush(heap, (wx, v, x))
    ms = (time.perf_counter() - t0) * 1000
    return MSTResult("Prim (heap)", chosen, total, comps <= 1, ms)


def prim_mst_dense(graph: Graph) -> MSTResult:
    t0 = time.perf_counter()
    n = graph.n
    inf = float("inf")
    mat = graph.matrix()
    visited = [False] * n
    key = [inf] * n
    parent = [-1] * n
    chosen, total, comps = [], 0.0, 0
    for start in range(n):
        if visited[start]:
            continue
        comps += 1
        key[start] = 0.0
        while True:
            u, best = -1, inf
            for i in range(n):
                if not visited[i] and key[i] < best:
                    u, best = i, key[i]
            if u == -1:
                break
            visited[u] = True
            if parent[u] != -1:
                chosen.append((parent[u], u, mat[parent[u]][u]))
                total += mat[parent[u]][u]
            row = mat[u]
            for v in range(n):
                if not visited[v] and row[v] < key[v]:
                    key[v] = row[v]
                    parent[v] = u
    ms = (time.perf_counter() - t0) * 1000
    return MSTResult("Prim (dense)", chosen, total, comps <= 1, ms)
