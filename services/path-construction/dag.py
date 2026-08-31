"""dag_builder / topo_sort — deterministic DAG ordering for a learning
path. Per ARCHITECTURE.md Section 03, card 05: "No language reasoning
needed." Stdlib-only Kahn's algorithm (heapq as the ready-set priority
queue) — no networkx dependency added for what's a handful of nodes.
"""

from __future__ import annotations

import heapq


def dag_builder(node_ids: list[str], dependency_edges: list[tuple[str, str]]) -> dict[str, list[str]]:
    """dependency_edges: list of (before_id, after_id) meaning before_id
    must come before after_id. Returns adjacency: {node: [nodes that come
    after it]}, restricted to node_ids actually present (and with
    self-edges dropped)."""
    node_set = set(node_ids)
    adjacency: dict[str, list[str]] = {n: [] for n in node_ids}
    for before, after in dependency_edges:
        if before in node_set and after in node_set and before != after:
            adjacency[before].append(after)
    return adjacency


def topo_sort(
    node_ids: list[str],
    adjacency: dict[str, list[str]],
    tie_break: dict[str, float] | None = None,
) -> list[str]:
    """Kahn's algorithm. `tie_break` (lower = earlier) resolves ordering
    among nodes with no dependency relationship between them — here,
    skill-gap priority rank, so a higher-priority gap's course still comes
    first when nothing in the dependency graph forces otherwise.

    Raises ValueError if the graph has a cycle (shouldn't happen with the
    hand-curated dependency data this is built against, but callers should
    have a fallback ordering ready rather than let this propagate)."""
    tie_break = tie_break or {}
    in_degree = {n: 0 for n in node_ids}
    for _src, dsts in adjacency.items():
        for d in dsts:
            in_degree[d] += 1

    heap = [(tie_break.get(n, 0), n) for n in node_ids if in_degree[n] == 0]
    heapq.heapify(heap)
    ordered: list[str] = []

    while heap:
        _, node = heapq.heappop(heap)
        ordered.append(node)
        for neighbor in adjacency.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, (tie_break.get(neighbor, 0), neighbor))

    if len(ordered) != len(node_ids):
        raise ValueError("Cycle detected in prerequisite graph — cannot topologically sort")

    return ordered
