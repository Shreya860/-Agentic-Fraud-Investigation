import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { dataService } from "../services/dataService";
import type { Transaction, RiskLevel } from "../types";
import Card from "../components/Card";
import Table, { type Column } from "../components/Table";
import { RiskBadge } from "../components/Badge";

export default function Transactions() {
  const navigate = useNavigate();
  const [txns, setTxns] = useState<Transaction[]>([]);
  const [q, setQ] = useState("");
  const [risk, setRisk] = useState<RiskLevel | "all">("all");
  const [channel, setChannel] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dataService.getTransactions().then((rows) => {
      setTxns(rows);
      setLoading(false);
    });
  }, []);

  const channels = useMemo(
    () => Array.from(new Set(txns.map((t) => t.channel))),
    [txns]
  );

  const filtered = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return txns.filter((t) => {
      if (risk !== "all" && t.riskLevel !== risk) return false;
      if (channel !== "all" && t.channel !== channel) return false;
      if (!ql) return true;
      return (
        t.transactionId.toLowerCase().includes(ql) ||
        t.customerName.toLowerCase().includes(ql) ||
        t.merchant.toLowerCase().includes(ql)
      );
    });
  }, [txns, q, risk, channel]);

  const columns: Column<Transaction>[] = [
    { key: "id",     header: "Transaction ID", render: (t) => <span className="mono">{t.transactionId}</span> },
    { key: "cust",   header: "Customer",       render: (t) => t.customerName },
    { key: "amount", header: "Amount",         render: (t) => `$${t.amount.toFixed(2)}`, align: "right" },
    { key: "chan",   header: "Channel",        render: (t) => t.channel },
    { key: "when",   header: "Timestamp",      render: (t) => new Date(t.timestamp).toLocaleString() },
    { key: "risk",   header: "Risk Score",     render: (t) => <span className="mono num">{(t.riskScore * 100).toFixed(0)}</span>, align: "right" },
    { key: "level",  header: "Risk Level",     render: (t) => <RiskBadge level={t.riskLevel} /> },
    { key: "status", header: "Status",         render: (t) => t.status },
  ];

  return (
    <div className="stack">
      <Card title="Transactions" subtitle={`${filtered.length} of ${txns.length} shown`} padded={false}>
        <div className="filter-bar">
          <input
            className="input"
            placeholder="Search ID, customer, merchant…"
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
          <select className="select" value={channel} onChange={(e) => setChannel(e.target.value)}>
            <option value="all">All channels</option>
            {channels.map((ch) => <option key={ch} value={ch}>{ch}</option>)}
          </select>
        </div>
        <Table
          columns={columns}
          rows={filtered}
          rowKey={(t) => t.transactionId}
          onRowClick={(t) => navigate(`/transactions/${t.transactionId}`)}
          emptyMessage={loading ? "Loading…" : "No transactions found"}
        />
      </Card>
    </div>
  );
}