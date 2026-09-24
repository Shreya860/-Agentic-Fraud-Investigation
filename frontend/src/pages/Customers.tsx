import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { dataService } from "../services/dataService";
import type { Customer, RiskLevel } from "../types";
import Card from "../components/Card";
import Table, { type Column } from "../components/Table";
import { RiskBadge } from "../components/Badge";

export default function Customers() {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [q, setQ] = useState("");
  const [risk, setRisk] = useState<RiskLevel | "all">("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dataService.getCustomers().then((rows) => {
      setCustomers(rows);
      setLoading(false);
    });
  }, []);

  const filtered = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return customers.filter((c) => {
      if (risk !== "all" && c.riskLevel !== risk) return false;
      if (!ql) return true;
      return (
        c.customerId.toLowerCase().includes(ql) ||
        c.name.toLowerCase().includes(ql) ||
        c.email.toLowerCase().includes(ql)
      );
    });
  }, [customers, q, risk]);

  const columns: Column<Customer>[] = [
    { key: "id",       header: "Customer ID",  render: (c) => <span className="mono">{c.customerId}</span> },
    { key: "name",     header: "Name",         render: (c) => c.name },
    { key: "risk",     header: "Risk Level",   render: (c) => <RiskBadge level={c.riskLevel} score={c.riskScore} /> },
    { key: "txns",     header: "Transactions", render: (c) => <span className="mono num">{c.transactionCount}</span>, align: "right" },
    { key: "devices",  header: "Devices",      render: (c) => <span className="mono num">{c.deviceCount}</span>, align: "right" },
    { key: "cards",    header: "Cards",        render: (c) => <span className="mono num">{c.cardCount}</span>, align: "right" },
    { key: "open",     header: "Open Cases",   render: (c) => <span className="mono num">{c.openCases}</span>, align: "right" },
    { key: "last",     header: "Last Activity", render: (c) => new Date(c.lastActivity).toLocaleString() },
  ];

  return (
    <div className="stack">
      <Card title="Customers" subtitle={`${filtered.length} of ${customers.length} shown`} padded={false}>
        <div className="filter-bar">
          <input
            className="input"
            placeholder="Search by ID, name, email…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            style={{ width: 280 }}
          />
          <select className="select" value={risk} onChange={(e) => setRisk(e.target.value as RiskLevel | "all")}>
            <option value="all">All risk levels</option>
            <option value="very_high">Very High</option>
            <option value="high">High</option>
            <option value="moderate">Moderate</option>
            <option value="low">Low</option>
          </select>
        </div>
        <Table
          columns={columns}
          rows={filtered}
          rowKey={(c) => c.customerId}
          onRowClick={(c) => navigate(`/customers/${c.customerId}`)}
          emptyMessage={loading ? "Loading…" : "No customers found"}
        />
      </Card>
    </div>
  );
}