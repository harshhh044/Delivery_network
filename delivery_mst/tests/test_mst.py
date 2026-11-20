import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mst import DisjointSet, Graph, kruskal_mst, prim_mst, prim_mst_dense
from mst import generators as gen

ALL = (prim_mst, prim_mst_dense, kruskal_mst)


def brute_force_mst_cost(g):
    """Exhaustive check: cheapest subset of n-1 edges forming a spanning tree."""
    from itertools import combinations
    best = float("inf")
    for combo in combinations(g.edges, g.n - 1):
        d = DisjointSet(g.n)
        if all(d.union(u, v) for u, v, _ in combo):
            best = min(best, sum(w for _, _, w in combo))
    return best


class TestDSU(unittest.TestCase):
    def test_union_find(self):
        d = DisjointSet(5)
        self.assertTrue(d.union(0, 1))
        self.assertFalse(d.union(1, 0))
        d.union(2, 3); d.union(1, 3)
        self.assertEqual(d.find(0), d.find(2))
        self.assertEqual(d.components, 2)


class TestKnownGraphs(unittest.TestCase):
    def setUp(self):
        # classic textbook graph, MST cost = 37
        self.g = Graph(list("ABCDEFGHI"))
        for u, v, w in [("A","B",4),("A","H",8),("B","C",8),("B","H",11),("C","D",7),
                        ("C","F",4),("C","I",2),("D","E",9),("D","F",14),("E","F",10),
                        ("F","G",2),("G","H",1),("G","I",6),("H","I",7)]:
            self.g.add_edge(u, v, w)

    def test_textbook_cost(self):
        for fn in ALL:
            r = fn(self.g)
            self.assertEqual(r.total_cost, 37, fn.__name__)
            self.assertEqual(len(r.edges), 8)
            self.assertTrue(r.connected)

    def test_result_is_spanning_tree(self):
        for fn in ALL:
            d = DisjointSet(self.g.n)
            for u, v, _ in fn(self.g).edges:
                self.assertTrue(d.union(u, v), "cycle found")
            self.assertEqual(d.components, 1)

    def test_sample_file(self):
        path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_network.json")
        g = Graph.from_json(path)
        costs = {round(fn(g).total_cost, 6) for fn in ALL}
        self.assertEqual(len(costs), 1)


class TestEdgeCases(unittest.TestCase):
    def test_single_vertex(self):
        g = Graph(["A"])
        for fn in ALL:
            r = fn(g)
            self.assertEqual((r.total_cost, r.edges, r.connected), (0.0, [], True))

    def test_two_vertices(self):
        g = Graph(["A", "B"]); g.add_edge("A", "B", 5)
        for fn in ALL:
            self.assertEqual(fn(g).total_cost, 5)

    def test_disconnected_gives_forest(self):
        g = Graph(list("ABCD")); g.add_edge("A", "B", 1); g.add_edge("C", "D", 2)
        for fn in ALL:
            r = fn(g)
            self.assertFalse(r.connected)
            self.assertEqual(r.total_cost, 3)

    def test_parallel_routes_keep_cheapest(self):
        g = Graph(["A", "B"]); g.add_edge("A", "B", 9); g.add_edge("B", "A", 4)
        self.assertEqual(g.m, 1)
        self.assertEqual(kruskal_mst(g).total_cost, 4)

    def test_equal_weights(self):
        g = gen.complete_network(6, 1)
        g.edges[:] = [(u, v, 1.0) for u, v, _ in g.edges]
        g._adj = None
        for fn in ALL:
            self.assertEqual(fn(g).total_cost, 5)

    def test_invalid_input(self):
        g = Graph(["A", "B"])
        with self.assertRaises(ValueError): g.add_edge("A", "A", 1)
        with self.assertRaises(ValueError): g.add_edge("A", "B", -1)
        with self.assertRaises(ValueError): g.add_vertex("A")


class TestRandomised(unittest.TestCase):
    def test_against_brute_force(self):
        for seed in range(30):
            n = random.Random(seed).randint(3, 6)
            g = gen.random_network(n, min(n * (n - 1) // 2, n + 3), seed)
            expected = brute_force_mst_cost(g)
            for fn in ALL:
                self.assertAlmostEqual(fn(g).total_cost, expected, places=6, msg=f"seed={seed} {fn.__name__}")

    def test_algorithms_agree_on_large_graphs(self):
        makers = [gen.sparse_network, gen.medium_network, gen.dense_network, gen.complete_network]
        for mk in makers:
            for seed in range(3):
                g = mk(80, seed)
                self.assertTrue(g.is_connected())
                costs = [fn(g).total_cost for fn in ALL]
                self.assertAlmostEqual(max(costs), min(costs), places=6)

    def test_city_and_grid(self):
        for g in (gen.city_network(60, seed=2), gen.grid_network(7, 8, seed=3)):
            self.assertTrue(g.is_connected())
            costs = [fn(g).total_cost for fn in ALL]
            self.assertAlmostEqual(max(costs), min(costs), places=6)
            self.assertEqual(len(prim_mst(g).edges), g.n - 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
