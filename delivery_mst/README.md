# Delivery Network Optimization Using Minimum Spanning Trees

Connects delivery locations with the **minimum total connection cost**.
Locations are vertices, possible routes are weighted edges. Prim's and Kruskal's
algorithms build the MST and are compared across different network configurations.

## Quick start
```bash
pip install -r requirements.txt        # only matplotlib, needed just for plots
python main.py demo                    # solve the sample network, save plots to output/
python -m unittest discover -s tests -v   # run all tests (standard library only)
python main.py benchmark               # compare Prim vs Kruskal
```

## Commands
| Command | What it does |
|---|---|
| `python main.py demo` | Solves `data/sample_network.json` with all algorithms, prints routes/cost, saves plots |
| `python main.py solve FILE.json [--no-plot]` | Solves your own network |
| `python main.py generate --type city --n 30 --out data/city30.json` | Creates a test network (`random, sparse, dense, complete, city, grid`) |
| `python main.py benchmark --sizes 100 300 600 --repeats 3 [--configs sparse dense]` | Runtime comparison, writes `output/benchmark_results.csv` and `benchmark_plot.png` |

## Input format (JSON)
```json
{"locations": [{"name": "Warehouse", "x": 50, "y": 50}, {"name": "Mall"}],
 "routes":    [{"from": "Warehouse", "to": "Mall", "cost": 36}]}
```
`x`/`y` are optional (used for plotting; otherwise vertices are drawn on a circle).
Duplicate routes keep the cheapest; negative costs and self-loops are rejected.

## Project layout
```
main.py              command-line interface
mst/graph.py         Graph + MSTResult, JSON load/save
mst/dsu.py           Union-Find (path compression + union by rank)
mst/kruskal.py       Kruskal, O(E log E)
mst/prim.py          Prim with heap O(E log V) and dense O(V^2) variants
mst/generators.py    sparse / medium / dense / complete / city / grid networks
mst/benchmark.py     timing + cross-checking of results
mst/visualize.py     network and benchmark plots
tests/test_mst.py    13 unit tests (incl. brute-force verification)
data/                sample network JSON
output/              generated plots and CSV
```

## How correctness is checked
* Textbook graph with a known MST cost (37).
* 30 random small graphs verified against exhaustive brute force.
* All algorithms must return the same cost on sparse/medium/dense/complete/city/grid graphs.
* Edge cases: single vertex, two vertices, disconnected network (returns a spanning forest and flags it), equal weights, invalid input.
* The benchmark itself raises an error if the algorithms ever disagree.

## Complexity
| Algorithm | Time | Best for |
|---|---|---|
| Kruskal | O(E log E) | sparse graphs |
| Prim (heap) | O(E log V) | sparse to medium graphs |
| Prim (dense) | O(V²) | dense / complete graphs |

## Sample benchmark observations (your timings will vary by machine)
* Sparse networks: Kruskal and heap-Prim are close; dense-Prim is slowest (O(V²) regardless of edges).
* Dense/complete networks: dense-Prim beats heap-Prim by roughly 6-10x, and is on par with Kruskal.
* Kruskal benefits from stopping early once V-1 edges are chosen.
* All algorithms always return the same MST cost (the tree itself can differ when weights tie).
