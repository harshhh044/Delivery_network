"""Graph model: delivery locations = vertices, possible routes = weighted edges."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

Edge = Tuple[int, int, float]  # (u_index, v_index, cost)


@dataclass
class MSTResult:
    algorithm: str
    edges: List[Edge]
    total_cost: float
    connected: bool            # False => result is a minimum spanning *forest*
    runtime_ms: float = 0.0


class Graph:
    """Undirected weighted graph. Vertices are identified by name (e.g. 'Warehouse')
    and stored internally as integer indices 0..n-1."""

    def __init__(self, names: Optional[List[str]] = None):
        self.names: List[str] = []
        self.index: Dict[str, int] = {}
        self.edges: List[Edge] = []
        self.coords: Dict[int, Tuple[float, float]] = {}
        self._adj: Optional[List[List[Tuple[int, float]]]] = None
        self._edge_pos: Dict[Tuple[int, int], int] = {}
        for n in names or []:
            self.add_vertex(n)

    # ---------- construction ----------
    @property
    def n(self) -> int:
        return len(self.names)

    @property
    def m(self) -> int:
        return len(self.edges)

    def has_edge(self, u: int, v: int) -> bool:
        return (min(u, v), max(u, v)) in self._edge_pos

    def add_vertex(self, name: str, coord: Optional[Tuple[float, float]] = None) -> int:
        if name in self.index:
            raise ValueError(f"Duplicate location: {name!r}")
        i = len(self.names)
        self.names.append(name)
        self.index[name] = i
        if coord is not None:
            self.coords[i] = (float(coord[0]), float(coord[1]))
        self._adj = None
        return i

    def add_edge(self, u, v, cost: float) -> None:
        """Add a route between u and v (names or indices). Parallel routes keep the cheapest."""
        ui = self.index[u] if isinstance(u, str) else u
        vi = self.index[v] if isinstance(v, str) else v
        if not (0 <= ui < self.n and 0 <= vi < self.n):
            raise ValueError("Unknown vertex")
        if ui == vi:
            raise ValueError("Self-loops are not allowed")
        if cost < 0:
            raise ValueError("Route cost cannot be negative")
        key = (min(ui, vi), max(ui, vi))
        if key in self._edge_pos:
            k = self._edge_pos[key]
            a, b, w = self.edges[k]
            if cost < w:
                self.edges[k] = (a, b, float(cost))
        else:
            self._edge_pos[key] = len(self.edges)
            self.edges.append((ui, vi, float(cost)))
        self._adj = None

    # ---------- views ----------
    @property
    def adj(self) -> List[List[Tuple[int, float]]]:
        if self._adj is None:
            adj: List[List[Tuple[int, float]]] = [[] for _ in range(self.n)]
            for u, v, w in self.edges:
                adj[u].append((v, w))
                adj[v].append((u, w))
            self._adj = adj
        return self._adj

    def matrix(self) -> List[List[float]]:
        inf = float("inf")
        mat = [[inf] * self.n for _ in range(self.n)]
        for u, v, w in self.edges:
            mat[u][v] = mat[v][u] = w
        return mat

    def is_connected(self) -> bool:
        if self.n <= 1:
            return True
        seen = {0}
        stack = [0]
        while stack:
            u = stack.pop()
            for v, _ in self.adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return len(seen) == self.n

    def total_cost(self) -> float:
        return sum(w for _, _, w in self.edges)

    def density(self) -> float:
        mx = self.n * (self.n - 1) / 2
        return self.m / mx if mx else 0.0

    # ---------- I/O ----------
    @classmethod
    def from_json(cls, path: str) -> "Graph":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        g = cls()
        for loc in data["locations"]:
            if isinstance(loc, str):
                g.add_vertex(loc)
            else:
                g.add_vertex(loc["name"], (loc["x"], loc["y"]) if "x" in loc else None)
        for r in data["routes"]:
            g.add_edge(r["from"], r["to"], r["cost"])
        return g

    def to_json(self, path: str) -> None:
        locs = []
        for i, name in enumerate(self.names):
            d = {"name": name}
            if i in self.coords:
                d["x"], d["y"] = self.coords[i]
            locs.append(d)
        routes = [{"from": self.names[u], "to": self.names[v], "cost": round(w, 4)}
                  for u, v, w in self.edges]
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"locations": locs, "routes": routes}, f, indent=2)
