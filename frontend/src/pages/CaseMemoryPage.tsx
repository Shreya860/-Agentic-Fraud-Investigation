import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { dataService } from "../services/dataService";
import type { HistoricalCase, RiskLevel } from "../types";
import Card from "../components/Card";
import Table, { type Column } from "../components/Table";
import Badge, { RiskBadge } from "../components/Badge";

const outcomeVariant: Record<HistoricalCase["outcome"], "danger" | "ok" | "neutral"> = {
  confirmed_fraud: "danger",
  false_positive: "ok",
  inconclusive: "neutral",
};

const outcomeLabel: Record<HistoricalCase["outcome"], string> = {
  confirmed_fraud: "Confirmed Fraud",
  false_positive: "False Positive",
  inconclusive: "Inconclusive",
};

export default function CaseMemoryPage() {
  const [cases, setCases] = useState<HistoricalCase[]>([]);
  const [q, setQ] = useState("");
  const [pattern, setPattern] = useState<string>("all");
  const [risk, setRisk] = useState<RiskLevel | "all">("all");
  const [outcome, setOutcome] = useState<HistoricalCase["outcome"] | "all">("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dataService.getHistoricalCases().then((rows) => {
      setCases(rows);
      setLoading(false);
    });
  }, []);

  const patterns = useMemo(
    () => Array.from(new Set(cases.map((c) => c.pattern))),
    [cases]
  );

  const filtered = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return cases.filter((c) => {
      if (pattern !== "all" && c.pattern !== pattern) return false;
      if (risk !== "all" && c.riskLevel !== risk) return false;
      if (outcome !== "all" && c.outcome !== outcome) return false;
      if (!ql) return true;
      return (
        c.caseId.toLowerCase().includes(ql) ||
        c.customerName.toLowerCase().includes(ql) ||
        c.summary.toLowerCase().includes(ql)
      );
    });
  }, [cases, q, pattern, risk, outcome]);

  const columns: Column<HistoricalCase>[] = [
    { key: "id",      header: "Case ID",  render: (c) => <span className="mono">{c.caseId}</span> },
    { key: "pattern", header: "Pattern",  render: (c) => c.pattern },
    { key: "cust",    header: "Customer", render: (c) => c.customerName },
    { key: "risk",    header: "Risk",     render: (c) => <RiskBadge level={c.riskLevel} /> },
    { key: "out",     header: "Outcome",  render: (c) => <Badge variant={outcomeVariant[c.outcome]}>{outcomeLabel[c.outcome]}</Badge> },
    { key: "sim",     header: "Similarity", render: (c) => <span className="mono">{(c.similarity * 100).toFixed(0)}%</span>, align: "right" },
  ];

  return (
    <div className="stack">
      <Card title="Case Memory" subtitle={`${filtered.length} of ${cases.length} cases`} padded={false}>
        <div className="filter-bar">
          <input
            className="input"
            placeholder="Search case ID, customer, summary…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            style={{ width: 280 }}
          />
          <select className="select" value={pattern} onChange={(e) => setPattern(e.target.value)}>
            <option value="all">All patterns</option>
            {patterns.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <select className="select" value={risk} onChange={(e) => setRisk(e.target.value as RiskLevel | "all")}>
            <option value="all">All risk levels</option>
            <option value="very_high">Very High</option>
            <option value="high">High</option>
            <option value="moderate">Moderate</option>
            <option value="low">Low</option>
          </select>
          <select className="select" value={outcome} onChange={(e) => setOutcome(e.target.value as HistoricalCase["outcome"] | "all")}>
            <option value="all">All outcomes</option>
            <option value="confirmed_fraud">Confirmed Fraud</option>
            <option value="false_positive">False Positive</option>
            <option value="inconclusive">Inconclusive</option>
          </select>
        </div>
        <Table
          columns={columns}
          rows={filtered}
          rowKey={(c) => c.caseId}
          emptyMessage={loading ? "Loading…" : "No historical cases found"}
        />
      </Card>

      <Card title="Case DNA — Pattern Breakdown" subtitle="Aggregated across historical cases">
        <div className="grid grid-2">
          {patterns.map((p) => {
            const group = cases.filter((c) => c.pattern === p);
            const avgSim = group.reduce((s, c) => s + c.similarity, 0) / Math.max(1, group.length);
            const confirmed = group.filter((c) => c.outcome === "confirmed_fraud").length;
            return (
              <div key={p} style={{ padding: 12, border: "1px solid var(--border)", borderRadius: 8 }}>
                <div className="row-between">
                  <strong>{p}</strong>
                  <Badge variant="neutral">{group.length} cases</Badge>
                </div>
                <div className="small muted mt-1">Avg similarity {(avgSim * 100).toFixed(0)}% · {confirmed} confirmed fraud</div>
              </div>
            );
          })}
        </div>
      </Card>

      <Card title="Recent Similar Cases" padded={false}>
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {filtered.slice(0, 5).map((c) => (
            <li key={c.caseId} style={{ padding: "10px 16px", borderBottom: "1px solid var(--border)" }}>
              <div className="row-between">
                <span className="mono">{c.caseId}</span>
                <span className="small muted">{c.pattern}</span>
                <Badge variant={outcomeVariant[c.outcome]}>{outcomeLabel[c.outcome]}</Badge>
                <span className="mono small">{(c.similarity * 100).toFixed(0)}%</span>
              </div>
              <div className="small muted mt-1">
                {c.summary} — <Link to={`/customers/${c.customerId}`}>{c.customerName}</Link>
              </div>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}