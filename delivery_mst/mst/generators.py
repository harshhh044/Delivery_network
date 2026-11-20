"""Network generators for experiments with different configurations."""
import math
import random

from .graph import Graph


def random_network(n: int, m: int, seed: int = 0, wmin=1.0, wmax=100.0) -> Graph:
    """Connected random graph with n locations and (about) m routes."""
    max_edges = n * (n - 1) // 2
    m = max(n - 1, min(m, max_edges))
    rng = random.Random(seed)
    g = Graph([f"L{i}" for i in range(n)])
    order = list(range(n))                       # random spanning tree => connected
    rng.shuffle(order)
    for i in range(1, n):
        g.add_edge(order[i], order[rng.randrange(i)], round(rng.uniform(wmin, wmax), 2))
    if m > max_edges * 0.6:                      # dense: enumerate then sample
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if not g.has_edge(i, j)]
        rng.shuffle(pairs)
        for i, j in pairs[: m - g.m]:
            g.add_edge(i, j, round(rng.uniform(wmin, wmax), 2))
    else:
        while g.m < m:
            i, j = rng.randrange(n), rng.randrange(n)
            if i != j and not g.has_edge(i, j):
                g.add_edge(i, j, round(rng.uniform(wmin, wmax), 2))
    return g


def sparse_network(n, seed=0):    return random_network(n, 2 * n, seed)
def medium_network(n, seed=0):    return random_network(n, int(0.25 * n * (n - 1) / 2), seed)
def dense_network(n, seed=0):     return random_network(n, int(0.75 * n * (n - 1) / 2), seed)
def complete_network(n, seed=0):  return random_network(n, n * (n - 1) // 2, seed)


def _components(g: Graph):
    seen, comps = set(), []
    for s in range(g.n):
        if s in seen:
            continue
        stack, comp = [s], []
        seen.add(s)
        while stack:
            u = stack.pop()
            comp.append(u)
            for v, _ in g.adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        comps.append(comp)
    return comps


def city_network(n: int, k: int = 6, seed: int = 0, size: float = 100.0) -> Graph:
    """Locations scattered on a 2D map; each connects to its k nearest neighbours
    (cost = Euclidean distance). Models a realistic road network."""
    rng = random.Random(seed)
    g = Graph()
    for i in range(n):
        g.add_vertex(f"L{i}", (rng.uniform(0, size), rng.uniform(0, size)))
    pts = [g.coords[i] for i in range(n)]
    dist = lambda a, b: math.dist(pts[a], pts[b])
    for i in range(n):
        near = sorted((j for j in range(n) if j != i), key=lambda j: dist(i, j))[:k]
        for j in near:
            g.add_edge(i, j, round(dist(i, j), 2))
    while not g.is_connected():                  # bridge components by closest pair
        comp = _components(g)
        base = comp[0]
        best = min((dist(a, b), a, b) for a in base for c in comp[1:] for b in c)
        g.add_edge(best[1], best[2], round(best[0], 2))
    return g


def grid_network(rows: int, cols: int, seed: int = 0) -> Graph:
    """Street-grid style network (Manhattan layout)."""
    rng = random.Random(seed)
    g = Graph()
    for r in range(rows):
        for c in range(cols):
            g.add_vertex(f"L{r}_{c}", (c * 10, r * 10))
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                g.add_edge(f"L{r}_{c}", f"L{r}_{c+1}", round(rng.uniform(1, 50), 2))
            if r + 1 < rows:
                g.add_edge(f"L{r}_{c}", f"L{r+1}_{c}", round(rng.uniform(1, 50), 2))
    return g
