import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { dataService } from "../services/dataService";
import type { InvestigationCase, RiskLevel, InvestigationStatus } from "../types";
import Card from "../components/Card";
import Table, { type Column } from "../components/Table";
import { RiskBadge, StatusBadge } from "../components/Badge";
import { actionLabels } from "../data/mockCases";

const triggerOptions = [
  "Customer Report",
  "Rule Engine",
  "Device Signal",
  "Amount Anomaly",
  "Behavioral",
];

const statusOptions: (InvestigationStatus | "all")[] = [
  "all",
  "open",
  "investigating",
  "awaiting_approval",
  "action_executed",
  "resolved",
  "closed",
];

const riskOptions: (RiskLevel | "all")[] = [
  "all",
  "very_high",
  "high",
  "moderate",
  "low",
];

export default function Investigations() {
  const navigate = useNavigate();
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState(true);

  const [q, setQ] = useState("");
  const [status, setStatus] = useState<InvestigationStatus | "all">("all");
  const [risk, setRisk] = useState<RiskLevel | "all">("all");
  const [trigger, setTrigger] = useState<string>("all");
  const [analyst, setAnalyst] = useState<string>("all");
  const [sortKey, setSortKey] = useState<"createdAt" | "riskScore">("createdAt");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  // Live list from backend benchmark outputs
  useEffect(() => {
    dataService
      .getInvestigations()
      .then((rows) => {
        setCases(rows);
      })
      .catch((err) => {
        console.error("getInvestigations failed:", err);
      })
      .finally(() => setLoading(false));
  }, []);

  const analysts = useMemo(
    () => Array.from(new Set(cases.map((c) => c.assignedAnalyst))),
    [cases]
  );

  const filtered = useMemo(() => {
    const ql = q.trim().toLowerCase();
    let rows = cases.filter((c) => {
      if (status !== "all" && c.status !== status) return false;
      if (risk !== "all" && c.riskLevel !== risk) return false;
      if (trigger !== "all" && c.triggerType !== trigger) return false;
      if (analyst !== "all" && c.assignedAnalyst !== analyst) return false;
      if (!ql) return true;
      return (
        c.caseId.toLowerCase().includes(ql) ||
        c.customerName.toLowerCase().includes(ql) ||
        c.triggerText.toLowerCase().includes(ql)
      );
    });
    rows = rows.sort((a, b) => {
      const av = sortKey === "createdAt" ? a.createdAt : a.riskScore;
      const bv = sortKey === "createdAt" ? b.createdAt : b.riskScore;
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
    return rows;
  }, [cases, q, status, risk, trigger, analyst, sortKey, sortDir]);

  const toggleSort = (key: "createdAt" | "riskScore") => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  const columns: Column<InvestigationCase>[] = [
    { key: "caseId",   header: "Case ID",          render: (c) => <span className="mono">{c.caseId}</span> },
    { key: "customer", header: "Customer",         render: (c) => c.customerName },
    { key: "trigger",  header: "Trigger",          render: (c) => c.triggerType },
    { key: "risk",     header: "Risk",             render: (c) => <RiskBadge level={c.riskLevel} /> },
    { key: "score",    header: "Risk Score",       align: "right",
      render: (c) => (
        <button
          className="btn btn-sm btn-ghost"
          onClick={(e) => { e.stopPropagation(); toggleSort("riskScore"); }}
          title="Sort by risk score"
        >
          {(c.riskScore * 100).toFixed(0)} {sortKey === "riskScore" && (sortDir === "desc" ? "↓" : "↑")}
        </button>
      ),
    },
    { key: "status",   header: "Status",           render: (c) => <StatusBadge status={c.status} /> },
    { key: "nba",      header: "Next Best Action",
      render: (c) => actionLabels[c.nextBestAction] || String(c.nextBestAction ?? "—"),
    },
    { key: "created",  header: "Created",          render: (c) => (
        <button
          className="btn btn-sm btn-ghost"
          onClick={(e) => { e.stopPropagation(); toggleSort("createdAt"); }}
          title="Sort by created date"
        >
          {new Date(c.createdAt).toLocaleDateString()} {sortKey === "createdAt" && (sortDir === "desc" ? "↓" : "↑")}
        </button>
      ),
    },
    { key: "analyst",  header: "Analyst",          render: (c) => c.assignedAnalyst },
  ];

  return (
    <div className="stack">
      <Card
        title="Investigations"
        subtitle={`${filtered.length} of ${cases.length} shown`}
        padded={false}
      >
        <div className="filter-bar">
          <input
            className="input"
            placeholder="Search case ID, customer, trigger…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            style={{ width: 260 }}
          />
          <select className="select" value={status} onChange={(e) => setStatus(e.target.value as InvestigationStatus | "all")}>
            {statusOptions.map((s) => (
              <option key={s} value={s}>{s === "all" ? "All statuses" : s.replace(/_/g, " ")}</option>
            ))}
          </select>
          <select className="select" value={risk} onChange={(e) => setRisk(e.target.value as RiskLevel | "all")}>
            {riskOptions.map((r) => (
              <option key={r} value={r}>{r === "all" ? "All risk" : r.replace(/_/g, " ")}</option>
            ))}
          </select>
          <select className="select" value={trigger} onChange={(e) => setTrigger(e.target.value)}>
            <option value="all">All triggers</option>
            {triggerOptions.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <select className="select" value={analyst} onChange={(e) => setAnalyst(e.target.value)}>
            <option value="all">All analysts</option>
            {analysts.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
          <button
            className="btn btn-sm"
            style={{ marginLeft: "auto" }}
            onClick={() => { setQ(""); setStatus("all"); setRisk("all"); setTrigger("all"); setAnalyst("all"); }}
          >
            Reset filters
          </button>
        </div>

        <Table
          columns={columns}
          rows={filtered}
          rowKey={(c) => c.caseId}
          onRowClick={(c) => navigate(`/investigations/${c.caseId}`)}
          emptyMessage={loading ? "Loading…" : "No investigations found"}
        />
      </Card>
    </div>
  );
}