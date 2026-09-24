import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { dataService } from "../services/dataService";
import type { InvestigationCase } from "../types";
import Card from "../components/Card";
import Table, { type Column } from "../components/Table";
import { RiskBadge, StatusBadge } from "../components/Badge";
import { BarChart, DonutChart, LineChart } from "../components/Charts";
import { actionLabels } from "../data/mockCases";

export default function Dashboard() {
  const navigate = useNavigate();
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    dataService.getInvestigations().then((rows) => {
      if (!alive) return;
      setCases(rows);
      setLoading(false);
    });
    return () => {
      alive = false;
    };
  }, []);

  const stats = useMemo(() => {
    const open = cases.filter((c) =>
      ["open", "investigating"].includes(c.status)
    ).length;
    const high = cases.filter(
      (c) => c.riskLevel === "high" || c.riskLevel === "very_high"
    ).length;
    const pending = cases.filter((c) => c.status === "awaiting_approval").length;
    const executed = cases.filter((c) => c.status === "action_executed").length;
    const resolved = cases.filter((c) => c.status === "resolved").length;

    // deterministic "avg investigation time" derived from case count
    const avgHours = cases.length === 0 ? 0 : (cases.length * 3.7).toFixed(1);

    return { open, high, pending, executed, resolved, avgHours };
  }, [cases]);

  const riskDistribution = useMemo(() => {
    const count = (level: string) =>
      cases.filter((c) => c.riskLevel === level).length;
    return [
      { label: "Very High", value: count("very_high"), color: "#b42318" },
      { label: "High",      value: count("high"),      color: "#b54708" },
      { label: "Moderate",  value: count("moderate"),  color: "#1d4ed8" },
      { label: "Low",       value: count("low"),       color: "#067647" },
    ];
  }, [cases]);

  const activityData = [
    { label: "Mon", value: 12 },
    { label: "Tue", value: 18 },
    { label: "Wed", value: 9 },
    { label: "Thu", value: 22 },
    { label: "Fri", value: 27 },
    { label: "Sat", value: 15 },
    { label: "Sun", value: 8 },
  ];

  const alerts = [
    { id: "A1", text: "New device shared across 4 accounts (DEV-88B2)", time: "9m ago", level: "very_high" as const },
    { id: "A2", text: "Wire transfer to high-risk jurisdiction flagged", time: "24m ago", level: "high" as const },
    { id: "A3", text: "Amount anomaly: 12x customer baseline",          time: "1h ago",  level: "high" as const },
    { id: "A4", text: "Card testing pattern detected (CUS-92017)",      time: "2h ago",  level: "moderate" as const },
  ];

  const recentCases = useMemo(
    () =>
      [...cases]
        .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
        .slice(0, 6),
    [cases]
  );

  const columns: Column<InvestigationCase>[] = [
    { key: "caseId",   header: "Case ID",  render: (c) => <span className="mono">{c.caseId}</span> },
    { key: "customer", header: "Customer", render: (c) => c.customerName },
    { key: "trigger",  header: "Trigger",  render: (c) => c.triggerType },
    { key: "risk",     header: "Risk",     render: (c) => <RiskBadge level={c.riskLevel} score={c.riskScore} /> },
    { key: "status",   header: "Status",   render: (c) => <StatusBadge status={c.status} /> },
    { key: "created",  header: "Created",  render: (c) => new Date(c.createdAt).toLocaleString() },
    { key: "analyst",  header: "Analyst",  render: (c) => c.assignedAnalyst },
  ];

  return (
    <div className="stack">
      <div className="grid grid-4">
        <Stat label="Open Investigations" value={stats.open} delta="+3 today" deltaClass="up" />
        <Stat label="High Risk Cases"     value={stats.high} delta="+2 today" deltaClass="up" />
        <Stat label="Pending Approvals"   value={stats.pending} delta="1 overdue" deltaClass="up" />
        <Stat label="Actions Executed"    value={stats.executed} delta="+5 this week" deltaClass="down" />
      </div>

      <div className="grid grid-4">
        <Stat label="Cases Resolved"           value={stats.resolved} delta="+8 this week" deltaClass="down" />
        <Stat label="Avg Investigation Time"   value={`${stats.avgHours}h`} delta="-0.4h vs last week" deltaClass="down" />
        <Stat label="Total Cases"              value={cases.length} delta="rolling 30d" />
        <Stat label="Analyst Coverage"         value="4/4" delta="all online" deltaClass="down" />
      </div>

      <Card title="Recent Investigations" subtitle="Latest 6 cases" padded={false}>
        <Table
          columns={columns}
          rows={recentCases}
          rowKey={(c) => c.caseId}
          onRowClick={(c) => navigate(`/investigations/${c.caseId}`)}
          emptyMessage={loading ? "Loading…" : "No investigations found"}
        />
      </Card>

      <div className="grid grid-2">
        <Card title="Risk Distribution" subtitle="Current open cases">
          <DonutChart slices={riskDistribution} />
        </Card>
        <Card title="Investigation Activity" subtitle="Last 7 days">
          <LineChart data={activityData} height={200} />
        </Card>
      </div>

      <div className="grid grid-2">
        <Card title="Alerts by Trigger" subtitle="Rolling 7 days">
          <BarChart
            data={[
              { label: "Rule",     value: 18 },
              { label: "Device",   value: 12 },
              { label: "Behavior", value: 9 },
              { label: "Customer", value: 7 },
              { label: "Amount",   value: 5 },
            ]}
          />
        </Card>
        <Card title="Recent Alerts" padded={false}>
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {alerts.map((a) => (
              <li
                key={a.id}
                style={{
                  padding: "12px 16px",
                  borderBottom: "1px solid var(--border)",
                }}
              >
                <div className="row-between">
                  <div className="row" style={{ gap: 8 }}>
                    <RiskBadge level={a.level} />
                    <span style={{ fontSize: 13 }}>{a.text}</span>
                  </div>
                  <span className="small muted">{a.time}</span>
                </div>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <Card title="Recommended Actions Summary" subtitle="Across open cases">
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {Object.entries(
            cases.reduce<Record<string, number>>((acc, c) => {
              const key = actionLabels[c.nextBestAction];
              acc[key] = (acc[key] ?? 0) + 1;
              return acc;
            }, {})
          ).map(([label, n]) => (
            <li key={label} className="row-between" style={{ padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
              <span>{label}</span>
              <span className="mono">{n}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

function Stat({
  label,
  value,
  delta,
  deltaClass,
}: {
  label: string;
  value: number | string;
  delta?: string;
  deltaClass?: "up" | "down";
}) {
  return (
    <div className="card stat">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {delta && <div className={`stat-delta ${deltaClass ?? ""}`}>{delta}</div>}
    </div>
  );
}