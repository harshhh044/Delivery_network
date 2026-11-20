#!/usr/bin/env python3
"""Delivery Network Optimization using Minimum Spanning Trees.

Usage examples:
  python main.py demo                       # solve the sample network + plots
  python main.py solve data/sample_network.json
  python main.py generate --type city --n 30 --out data/city30.json
  python main.py benchmark                  # compare Prim vs Kruskal
  python main.py benchmark --sizes 100 300 600 --repeats 3
"""
import argparse
import os
import sys

from mst import Graph, kruskal_mst, prim_mst, prim_mst_dense
from mst import generators as gen
from mst.benchmark import CONFIGS, print_table, run_benchmark, save_csv
from mst.visualize import plot_benchmark, plot_network

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")


def report(graph, result):
    print(f"\n=== {result.algorithm} ===")
    if not result.connected:
        print("WARNING: network is disconnected - showing minimum spanning forest")
    for u, v, w in sorted(result.edges, key=lambda e: e[2]):
        print(f"  {graph.names[u]:<14} <-> {graph.names[v]:<14} cost {w:g}")
    print(f"  Total connection cost : {result.total_cost:g}")
    print(f"  Routes used           : {len(result.edges)} of {graph.m}")
    print(f"  Cost saved vs all routes: {graph.total_cost() - result.total_cost:g}")
    print(f"  Runtime               : {result.runtime_ms:.4f} ms")


def solve(graph, plot=True, tag="network"):
    os.makedirs(OUT, exist_ok=True)
    print(f"Network: {graph.n} locations, {graph.m} routes, connected={graph.is_connected()}")
    results = [prim_mst(graph), prim_mst_dense(graph), kruskal_mst(graph)]
    for r in results:
        report(graph, r)
    costs = {round(r.total_cost, 6) for r in results}
    print("\nVerification: all algorithms give the same MST cost ->", "OK" if len(costs) == 1 else "MISMATCH")
    if plot:
        for r, name in ((results[0], "prim"), (results[2], "kruskal")):
            p = os.path.join(OUT, f"{tag}_{name}_mst.png")
            if plot_network(graph, r.edges, p, f"{r.algorithm} MST - total cost {r.total_cost:g}"):
                print("Saved plot:", p)
    return results


def cmd_benchmark(a):
    os.makedirs(OUT, exist_ok=True)
    rows = run_benchmark(sizes=tuple(a.sizes), configs=a.configs, repeats=a.repeats, seed=a.seed)
    print_table(rows)
    csv_path = os.path.join(OUT, "benchmark_results.csv")
    save_csv(rows, csv_path)
    print("Saved:", csv_path)
    png = os.path.join(OUT, "benchmark_plot.png")
    if plot_benchmark(rows, png):
        print("Saved:", png)


def cmd_generate(a):
    makers = {
        "random": lambda: gen.random_network(a.n, a.m or 3 * a.n, a.seed),
        "sparse": lambda: gen.sparse_network(a.n, a.seed),
        "dense": lambda: gen.dense_network(a.n, a.seed),
        "complete": lambda: gen.complete_network(a.n, a.seed),
        "city": lambda: gen.city_network(a.n, seed=a.seed),
        "grid": lambda: gen.grid_network(int(a.n ** 0.5), int(a.n ** 0.5), a.seed),
    }
    g = makers[a.type]()
    g.to_json(a.out)
    print(f"Generated {a.type} network: {g.n} locations, {g.m} routes -> {a.out}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("demo", help="solve the bundled sample network")
    s = sub.add_parser("solve", help="solve a network from a JSON file")
    s.add_argument("file"); s.add_argument("--no-plot", action="store_true")

    b = sub.add_parser("benchmark", help="compare Prim and Kruskal")
    b.add_argument("--sizes", type=int, nargs="+", default=[50, 100, 200, 400])
    b.add_argument("--configs", nargs="+", choices=list(CONFIGS), default=None)
    b.add_argument("--repeats", type=int, default=5)
    b.add_argument("--seed", type=int, default=1)

    g = sub.add_parser("generate", help="generate a test network JSON")
    g.add_argument("--type", choices=["random", "sparse", "dense", "complete", "city", "grid"], default="city")
    g.add_argument("--n", type=int, default=30)
    g.add_argument("--m", type=int, default=None)
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--out", default=os.path.join(HERE, "data", "generated.json"))

    a = p.parse_args(argv)
    if a.cmd == "demo":
        solve(Graph.from_json(os.path.join(HERE, "data", "sample_network.json")), tag="sample")
    elif a.cmd == "solve":
        solve(Graph.from_json(a.file), plot=not a.no_plot, tag=os.path.splitext(os.path.basename(a.file))[0])
    elif a.cmd == "benchmark":
        cmd_benchmark(a)
    elif a.cmd == "generate":
        cmd_generate(a)


if __name__ == "__main__":
    sys.exit(main())
