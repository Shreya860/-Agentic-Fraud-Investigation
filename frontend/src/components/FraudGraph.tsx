import { useMemo, useState } from "react";
import type { GraphData, GraphNode } from "../types";
import { ZoomIn, ZoomOut, RotateCcw } from "lucide-react";
import EmptyState from "./EmptyState";

interface Props {
  data: GraphData;
  selectedId?: string | null;
  onSelect?: (id: string | null) => void;
  height?: number;
}

const typeColor: Record<GraphNode["type"], string> = {
  customer:    "#1d4ed8",
  transaction: "#b54708",
  card:        "#067647",
  device:      "#7a5af8",
  identity:    "#b42318",
  case:        "#344054",
};

const typeLabel: Record<GraphNode["type"], string> = {
  customer:    "Customer",
  transaction: "Transaction",
  card:        "Card",
  device:      "Device",
  identity:    "Identity",
  case:        "Case",
};

export default function FraudGraph({
  data,
  selectedId,
  onSelect,
  height = 420,
}: Props) {
  const [zoom, setZoom] = useState(1);

  const { nodes, edges } = data;
  const byId = useMemo(() => {
    const m = new Map<string, GraphNode>();
    nodes.forEach((n) => m.set(n.id, n));
    return m;
  }, [nodes]);

  if (nodes.length === 0) {
    return (
      <div className="graph-wrap" style={{ height }}>
        <EmptyState title="No graph relationships found" subtitle="Nothing to display for this case." />
      </div>
    );
  }

  const W = 800;
  const H = 480;
  const scale = zoom;

  return (
    <div className="graph-wrap" style={{ height }}>
      <div className="graph-controls">
        <button className="btn btn-sm" onClick={() => setZoom((z) => Math.min(2.5, z + 0.15))} aria-label="Zoom in">
          <ZoomIn size={14} />
        </button>
        <button className="btn btn-sm" onClick={() => setZoom((z) => Math.max(0.5, z - 0.15))} aria-label="Zoom out">
          <ZoomOut size={14} />
        </button>
        <button className="btn btn-sm" onClick={() => { setZoom(1); onSelect?.(null); }} aria-label="Reset">
          <RotateCcw size={14} />
        </button>
      </div>

      <svg
        className="graph-svg"
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="xMidYMid meet"
      >
        <g transform={`translate(${W / 2} ${H / 2}) scale(${scale}) translate(${-W / 2} ${-H / 2})`}>
          {/* edges */}
          {edges.map((e) => {
            const a = byId.get(e.from);
            const b = byId.get(e.to);
            if (!a || !b) return null;
            const x1 = a.x * W;
            const y1 = a.y * H;
            const x2 = b.x * W;
            const y2 = b.y * H;
            const mx = (x1 + x2) / 2;
            const my = (y1 + y2) / 2;
            return (
              <g key={e.id}>
                <line
                  x1={x1} y1={y1} x2={x2} y2={y2}
                  stroke="var(--border-strong)"
                  strokeWidth={1.2}
                />
                <text
                  x={mx} y={my - 4}
                  fontSize={10}
                  textAnchor="middle"
                  fill="var(--text-3)"
                >
                  {e.label}
                </text>
              </g>
            );
          })}

          {/* nodes */}
          {nodes.map((n) => {
            const cx = n.x * W;
            const cy = n.y * H;
            const selected = selectedId === n.id;
            return (
              <g
                key={n.id}
                className={`graph-node ${selected ? "selected" : ""}`}
                transform={`translate(${cx} ${cy})`}
                onClick={() => onSelect?.(selected ? null : n.id)}
              >
                <circle r={22} fill={typeColor[n.type]} opacity={0.14} />
                <circle r={16} fill="#fff" stroke={typeColor[n.type]} strokeWidth={2} />
                <circle r={4}  fill={typeColor[n.type]} />
                <text
                  y={36}
                  fontSize={11}
                  textAnchor="middle"
                  fill="var(--text)"
                  fontWeight={600}
                >
                  {n.label}
                </text>
                <text
                  y={48}
                  fontSize={9}
                  textAnchor="middle"
                  fill="var(--text-3)"
                >
                  {typeLabel[n.type]}
                </text>
              </g>
            );
          })}
        </g>
      </svg>

      <div className="graph-legend">
        {(Object.keys(typeLabel) as GraphNode["type"][]).map((t) => (
          <div key={t} className="graph-legend-row">
            <span className="graph-legend-dot" style={{ background: typeColor[t] }} />
            <span>{typeLabel[t]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}