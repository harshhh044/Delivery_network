"""Benchmark Prim (heap), Prim (dense) and Kruskal on different network configurations."""
import csv
import statistics

from . import generators as gen
from .kruskal import kruskal_mst
from .prim import prim_mst, prim_mst_dense

ALGOS = [("Prim (heap)", prim_mst), ("Prim (dense)", prim_mst_dense), ("Kruskal", kruskal_mst)]
CONFIGS = {
    "sparse":   gen.sparse_network,
    "medium":   gen.medium_network,
    "dense":    gen.dense_network,
    "complete": gen.complete_network,
}


def time_algo(fn, graph, repeats=5):
    """Return (median_ms, total_cost)."""
    times, cost = [], None
    for _ in range(repeats):
        r = fn(graph)
        times.append(r.runtime_ms)
        cost = r.total_cost
    return statistics.median(times), cost


def run_benchmark(sizes=(50, 100, 200, 400), configs=None, repeats=5, seed=1):
    """Returns list of row dicts. Also asserts all algorithms agree on MST cost."""
    rows = []
    for cname in (configs or CONFIGS):
        for n in sizes:
            g = CONFIGS[cname](n, seed)
            costs = {}
            row = {"config": cname, "V": g.n, "E": g.m, "density": round(g.density(), 3)}
            for name, fn in ALGOS:
                ms, cost = time_algo(fn, g, repeats)
                row[name] = round(ms, 3)
                costs[name] = cost
            vals = list(costs.values())
            if max(vals) - min(vals) > 1e-6 * max(1.0, abs(vals[0])):
                raise AssertionError(f"Algorithms disagree on {cname} n={n}: {costs}")
            row["mst_cost"] = round(vals[0], 2)
            row["winner"] = min(ALGOS, key=lambda a: row[a[0]])[0]
            rows.append(row)
    return rows


def print_table(rows):
    hdr = f"{'Config':<9}{'V':>6}{'E':>8}{'Dens':>7}{'Prim-heap':>12}{'Prim-dense':>12}{'Kruskal':>11}{'MST cost':>11}  Winner"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['config']:<9}{r['V']:>6}{r['E']:>8}{r['density']:>7.2f}"
              f"{r['Prim (heap)']:>12.3f}{r['Prim (dense)']:>12.3f}{r['Kruskal']:>11.3f}"
              f"{r['mst_cost']:>11.2f}  {r['winner']}")
    print("(times in milliseconds, median of repeated runs)")


def save_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
