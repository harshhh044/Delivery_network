"""Matplotlib visualisations (optional dependency)."""
import math

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except ImportError:          # pragma: no cover
    HAVE_MPL = False


def _layout(graph):
    """Use real coordinates if present, else place vertices on a circle."""
    if len(graph.coords) == graph.n:
        return {i: graph.coords[i] for i in range(graph.n)}
    return {i: (math.cos(2 * math.pi * i / graph.n), math.sin(2 * math.pi * i / graph.n))
            for i in range(graph.n)}


def plot_network(graph, mst_edges, path, title="Delivery network", show_weights=True):
    if not HAVE_MPL:
        print("matplotlib not installed - skipping plot:", path)
        return False
    pos = _layout(graph)
    in_mst = {(min(u, v), max(u, v)) for u, v, _ in mst_edges}
    fig, ax = plt.subplots(figsize=(9, 7))
    for u, v, w in graph.edges:
        if (min(u, v), max(u, v)) in in_mst:
            continue
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color="#cccccc", lw=0.8, zorder=1)
    for u, v, w in mst_edges:
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color="#d62728", lw=2.4, zorder=2)
        if show_weights and graph.n <= 25:
            ax.text((pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2, f"{w:g}",
                    fontsize=8, color="#7a1010", ha="center",
                    bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.5), zorder=4)
    xs, ys = zip(*[pos[i] for i in range(graph.n)])
    ax.scatter(xs, ys, s=120 if graph.n <= 25 else 30, color="#1f77b4", zorder=3, edgecolor="white")
    if graph.n <= 25:
        span = (max(ys) - min(ys)) or 1.0
        for i in range(graph.n):
            ax.annotate(graph.names[i], pos[i], xytext=(0, -11), textcoords="offset points",
                        fontsize=8, ha="center", va="top", color="#111111", zorder=5,
                        bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.6))
    ax.set_title(title)
    ax.axis("equal"); ax.axis("off")
    ax.plot([], [], color="#d62728", lw=2.4, label="MST route (selected)")
    ax.plot([], [], color="#cccccc", lw=1, label="Unused route")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return True


def plot_benchmark(rows, path):
    if not HAVE_MPL:
        print("matplotlib not installed - skipping plot:", path)
        return False
    configs = list(dict.fromkeys(r["config"] for r in rows))
    fig, axes = plt.subplots(1, len(configs), figsize=(4.2 * len(configs), 4), sharey=False)
    if len(configs) == 1:
        axes = [axes]
    styles = {"Prim (heap)": ("#1f77b4", "o"), "Prim (dense)": ("#2ca02c", "s"), "Kruskal": ("#d62728", "^")}
    for ax, c in zip(axes, configs):
        sub = [r for r in rows if r["config"] == c]
        for algo, (col, mk) in styles.items():
            ax.plot([r["V"] for r in sub], [r[algo] for r in sub], marker=mk, color=col, label=algo)
        ax.set_title(f"{c} (density≈{sub[0]['density']:.2f}+)")
        ax.set_xlabel("Vertices"); ax.set_ylabel("Time (ms)"); ax.grid(alpha=0.3)
    axes[0].legend()
    fig.suptitle("Prim vs Kruskal runtime")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return True
