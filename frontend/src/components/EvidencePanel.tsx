import { useState } from "react";
import type { EvidenceCategory, EvidenceItem } from "../types";
import Badge from "./Badge";
import EmptyState from "./EmptyState";

interface Props {
  items: EvidenceItem[];
}

const categories: { id: EvidenceCategory | "all"; label: string }[] = [
  { id: "all",         label: "All" },
  { id: "transaction", label: "Transaction" },
  { id: "customer",    label: "Customer" },
  { id: "card",        label: "Card" },
  { id: "device",      label: "Device" },
  { id: "identity",    label: "Identity" },
  { id: "behavioral",  label: "Behavioral" },
  { id: "historical",  label: "Historical" },
  { id: "external",    label: "External" },
];

function typeBadge(type: EvidenceItem["type"]) {
  switch (type) {
    case "supporting":   return <Badge variant="danger">Supporting</Badge>;
    case "contradicting":return <Badge variant="ok">Contradicting</Badge>;
    default:             return <Badge variant="neutral">Neutral</Badge>;
  }
}

export default function EvidencePanel({ items }: Props) {
  const [active, setActive] = useState<EvidenceCategory | "all">("all");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const filtered =
    active === "all" ? items : items.filter((i) => i.category === active);

  return (
    <section className="card">
      <header className="card-header">
        <h2>Evidence</h2>
        <span className="card-title-sub">{items.length} items</span>
      </header>

      <div className="filter-bar" style={{ borderTop: 0 }}>
        {categories.map((c) => (
          <button
            key={c.id}
            className={`btn btn-sm ${active === c.id ? "btn-primary" : "btn-ghost"}`}
            onClick={() => setActive(c.id)}
          >
            {c.label}
          </button>
        ))}
      </div>

      <div className="card-body">
        {filtered.length === 0 ? (
          <EmptyState
            title="No evidence found"
            subtitle="No evidence items match the selected category."
          />
        ) : (
          filtered.map((ev) => (
            <div key={ev.id} className="evidence-item">
              <div className="evidence-head">
                {typeBadge(ev.type)}
                <span className="evidence-title">{ev.title}</span>
                <button
                  className="btn btn-sm btn-ghost"
                  style={{ marginLeft: "auto" }}
                  onClick={() =>
                    setExpanded((e) => ({ ...e, [ev.id]: !e[ev.id] }))
                  }
                >
                  {expanded[ev.id] ? "Hide" : "Details"}
                </button>
              </div>
              <div className="evidence-desc">{ev.description}</div>
              <div className="evidence-meta">
                <span>Category: {ev.category}</span>
                <span>Confidence: {ev.confidence}</span>
                <span>Source: {ev.source}</span>
                <span>{new Date(ev.timestamp).toLocaleString()}</span>
              </div>
              {expanded[ev.id] && (
                <pre
                  className="mono"
                  style={{
                    background: "var(--surface-2)",
                    padding: 10,
                    borderRadius: 6,
                    marginTop: 8,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {JSON.stringify(ev, null, 2)}
                </pre>
              )}
            </div>
          ))
        )}
      </div>
    </section>
  );
}