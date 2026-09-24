import { useEffect, useMemo, useState } from "react";
import { dataService } from "../services/dataService";
import type { GraphData, GraphNode } from "../types";
import Card from "../components/Card";
import FraudGraph from "../components/FraudGraph";
import Badge from "../components/Badge";
import EmptyState from "../components/EmptyState";
import { useApp } from "../context/AppContext";

type TypeFilter = GraphNode["type"] | "all";

const typeLabels: Record<GraphNode["type"], string> = {
  customer: "Customer",
  transaction: "Transaction",
  card: "Card",
  device: "Device",
  identity: "Identity",
  case: "Fraud Case",
};

export default function KnowledgeGraph() {
  const { selectedGraphNodeId, setSelectedGraphNodeId } = useApp();
  const [graph, setGraph] = useState<GraphData>({ nodes: [], edges: [] });
  const [q, setQ] = useState("");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("all");
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    dataService.getGraphData("CASE-48291").then(setGraph);
  }, []);

  const filtered: GraphData = useMemo(() => {
    const ql = q.trim().toLowerCase();
    const keep = new Set(
      graph.nodes
        .filter((n) => {
          if (typeFilter !== "all" && n.type !== typeFilter) return false;
          if (ql && !n.label.toLowerCase().includes(ql) && !n.id.toLowerCase().includes(ql)) return false;
          return true;
        })
        .map((n) => n.id)
    );
    // When the user filters, keep any matching node AND its direct neighbours
    // so edges still make sense.
    const expandedKeep = new Set(keep);
    graph.edges.forEach((e) => {
      if (keep.has(e.from)) expandedKeep.add(e.to);
      if (keep.has(e.to)) expandedKeep.add(e.from);
    });
    const active = expanded ? keep : expandedKeep;
    return {
      nodes: graph.nodes.filter((n) => active.has(n.id)),
      edges: graph.edges.filter((e) => active.has(e.from) && active.has(e.to)),
    };
  }, [graph, q, typeFilter, expanded]);

  const selectedNode = graph.nodes.find((n) => n.id === selectedGraphNodeId) ?? null;

  const neighbours = useMemo(() => {
    if (!selectedNode) return [];
    return graph.edges
      .filter((e) => e.from === selectedNode.id || e.to === selectedNode.id)
      .map((e) => {
        const otherId = e.from === selectedNode.id ? e.to : e.from;
        const other = graph.nodes.find((n) => n.id === otherId);
        return { edge: e, node: other ?? null };
      })
      .filter((x) => x.node !== null) as { edge: typeof graph.edges[0]; node: GraphNode }[];
  }, [graph, selectedNode]);

  return (
    <div className="grid" style={{ gridTemplateColumns: "220px 1fr 300px", gap: 16, alignItems: "start" }}>
      {/* Left filter sidebar */}
      <Card title="Filters" padded>
        <div className="section-title">Entity type</div>
        <div className="stack" style={{ gap: 4 }}>
          {(["all", "customer", "transaction", "card", "device", "identity", "case"] as TypeFilter[]).map((t) => (
            <button
              key={t}
              className={`btn btn-sm ${typeFilter === t ? "btn-primary" : "btn-ghost"}`}
              style={{ justifyContent: "flex-start" }}
              onClick={() => setTypeFilter(t)}
            >
              {t === "all" ? "All entities" : typeLabels[t]}
            </button>
          ))}
        </div>

        <div className="divider" />

        <div className="section-title">Search entity</div>
        <input
          className="input"
          placeholder="ID or label…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{ width: "100%" }}
        />

        <div className="divider" />

        <label className="row small" style={{ gap: 6 }}>
          <input
            type="checkbox"
            checked={expanded}
            onChange={(e) => setExpanded(e.target.checked)}
          />
          Only direct matches
        </label>

        <div className="divider" />

        <div className="row" style={{ gap: 8 }}>
          <button className="btn btn-sm" onClick={() => { setQ(""); setTypeFilter("all"); setSelectedGraphNodeId(null); setExpanded(false); }}>
            Reset graph
          </button>
        </div>
      </Card>

      {/* Main graph */}
      <Card title="Knowledge Graph" subtitle={`${filtered.nodes.length} nodes · ${filtered.edges.length} edges`} padded>
        {filtered.nodes.length === 0 ? (
          <EmptyState title="No graph relationships found" subtitle="Adjust filters or clear the search." />
        ) : (
          <FraudGraph
            data={filtered}
            selectedId={selectedGraphNodeId}
            onSelect={setSelectedGraphNodeId}
            height={560}
          />
        )}
      </Card>

      {/* Right selected-entity panel */}
      <Card title="Entity Details" padded>
        {!selectedNode ? (
          <div className="small muted">Select a node to view details.</div>
        ) : (
          <div>
            <div className="row-between mb-3">
              <div>
                <div className="section-title">Label</div>
                <div style={{ fontWeight: 600 }}>{selectedNode.label}</div>
              </div>
              <Badge variant="neutral">{typeLabels[selectedNode.type]}</Badge>
            </div>
            <dl className="kv" style={{ gridTemplateColumns: "90px 1fr" }}>
              <dt>ID</dt><dd className="mono">{selectedNode.id}</dd>
              <dt>Type</dt><dd>{selectedNode.type}</dd>
              <dt>Position</dt><dd className="mono">x={selectedNode.x.toFixed(2)} y={selectedNode.y.toFixed(2)}</dd>
            </dl>

            <div className="divider" />

            <div className="section-title">Relationships ({neighbours.length})</div>
            {neighbours.length === 0 ? (
              <div className="small muted">No relationships.</div>
            ) : (
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {neighbours.map(({ edge, node }) => (
                  <li
                    key={edge.id}
                    style={{ padding: "6px 0", borderBottom: "1px solid var(--border)", cursor: "pointer" }}
                    onClick={() => setSelectedGraphNodeId(node.id)}
                  >
                    <div className="row-between">
                      <span className="small">{edge.label}</span>
                      <span className="mono small">{node.label}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}

            <div className="divider" />

            <button
              className="btn btn-sm"
              style={{ width: "100%" }}
              onClick={() => setSelectedGraphNodeId(null)}
            >
              Clear selection
            </button>
          </div>
        )}
      </Card>
    </div>
  );
}