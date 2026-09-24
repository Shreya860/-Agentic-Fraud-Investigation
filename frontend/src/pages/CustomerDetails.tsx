import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { dataService } from "../services/dataService";
import type {
  Customer,
  Transaction,
  Card as CardT,
  Device,
  Identity,
  InvestigationCase,
  HistoricalCase,
  GraphData,
} from "../types";
import Card from "../components/Card";
import Table, { type Column } from "../components/Table";
import Badge, { RiskBadge, StatusBadge } from "../components/Badge";
import EmptyState from "../components/EmptyState";
import FraudGraph from "../components/FraudGraph";
import CaseMemory from "../components/CaseMemory";
import { useApp } from "../context/AppContext";

export default function CustomerDetails() {
  const { customerId = "" } = useParams<{ customerId: string }>();
  const { selectedGraphNodeId, setSelectedGraphNodeId } = useApp();

  const [c, setC] = useState<Customer | null | undefined>(undefined);
  const [txns, setTxns] = useState<Transaction[]>([]);
  const [cards, setCards] = useState<CardT[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [identities, setIdentities] = useState<Identity[]>([]);
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [history, setHistory] = useState<HistoricalCase[]>([]);
  const [graph, setGraph] = useState<GraphData>({ nodes: [], edges: [] });

  useEffect(() => {
    let alive = true;
    Promise.all([
      dataService.getCustomer(customerId),
      dataService.getTransactions(),
      dataService.getCardsForCustomer(customerId),
      dataService.getDevicesForCustomer(customerId),
      dataService.getIdentitiesForCustomer(customerId),
      dataService.getInvestigations(),
      dataService.getHistoricalCases(),
      dataService.getGraphData("CASE-48291"),
    ]).then(([cu, tx, cd, dv, id, cs, hi, gr]) => {
      if (!alive) return;
      setC(cu ?? null);
      setTxns(tx.filter((t) => t.customerId === customerId));
      setCards(cd);
      setDevices(dv);
      setIdentities(id);
      setCases(cs.filter((x) => x.customerId === customerId));
      setHistory(hi.filter((h) => h.customerId === customerId));
      setGraph(gr);
    });
    return () => {
      alive = false;
    };
  }, [customerId]);

  if (c === undefined) return <div className="muted">Loading customer…</div>;
  if (c === null) return <EmptyState title="Customer not found" subtitle={`No customer with id ${customerId}`} />;

  const txnCols: Column<Transaction>[] = [
    { key: "id",     header: "Transaction",  render: (t) => <Link to={`/transactions/${t.transactionId}`} className="mono">{t.transactionId}</Link> },
    { key: "amount", header: "Amount",       render: (t) => `$${t.amount.toFixed(2)}`, align: "right" },
    { key: "chan",   header: "Channel",      render: (t) => t.channel },
    { key: "when",   header: "Timestamp",    render: (t) => new Date(t.timestamp).toLocaleString() },
    { key: "risk",   header: "Risk",         render: (t) => <RiskBadge level={t.riskLevel} score={t.riskScore} /> },
  ];

  return (
    <div className="stack">
      <div className="card" style={{ padding: 16 }}>
        <div className="row-between">
          <div>
            <h1 style={{ fontSize: 18 }}>{c.name}</h1>
            <div className="small muted mt-1">
              <span className="mono">{c.customerId}</span> · {c.email} · {c.country} · account age {c.accountAgeYears}y
            </div>
          </div>
          <RiskBadge level={c.riskLevel} score={c.riskScore} />
        </div>
      </div>

      <div className="grid grid-4">
        <div className="card stat"><div className="stat-label">Transactions</div><div className="stat-value">{c.transactionCount}</div></div>
        <div className="card stat"><div className="stat-label">Devices</div><div className="stat-value">{c.deviceCount}</div></div>
        <div className="card stat"><div className="stat-label">Cards</div><div className="stat-value">{c.cardCount}</div></div>
        <div className="card stat"><div className="stat-label">Open Cases</div><div className="stat-value">{c.openCases}</div></div>
      </div>

      <Card title="Profile">
        <dl className="kv">
          <dt>Customer ID</dt><dd className="mono">{c.customerId}</dd>
          <dt>Email</dt><dd>{c.email}</dd>
          <dt>Country</dt><dd>{c.country}</dd>
          <dt>Account Age</dt><dd>{c.accountAgeYears} years</dd>
          <dt>Last Activity</dt><dd>{new Date(c.lastActivity).toLocaleString()}</dd>
        </dl>
      </Card>

      <Card title="Transaction History" padded={false}>
        <Table columns={txnCols} rows={txns} rowKey={(t) => t.transactionId} emptyMessage="No transactions found" />
      </Card>

      <div className="grid grid-2">
        <Card title="Cards">
          {cards.length === 0 ? (
            <EmptyState title="No cards" />
          ) : (
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              {cards.map((cd) => (
                <li key={cd.cardId} className="row-between" style={{ padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                  <span className="mono">•••• {cd.last4}</span>
                  <span className="small muted">{cd.network} {cd.type}</span>
                  <Badge variant={cd.status === "active" ? "ok" : cd.status === "frozen" ? "warn" : "danger"}>{cd.status}</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Devices">
          {devices.length === 0 ? (
            <EmptyState title="No devices" />
          ) : (
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              {devices.map((d) => (
                <li key={d.deviceId} style={{ padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                  <div className="row-between">
                    <span className="mono">{d.deviceId}</span>
                    <span className="small muted">{d.os}</span>
                    <Badge variant={d.linkedCustomers > 1 ? "danger" : "neutral"}>
                      {d.linkedCustomers} customer{d.linkedCustomers === 1 ? "" : "s"}
                    </Badge>
                  </div>
                  <div className="small muted mt-1">fingerprint {d.fingerprint}</div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <div className="grid grid-2">
        <Card title="Identity Signals">
          {identities.length === 0 ? (
            <EmptyState title="No identity signals" />
          ) : (
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              {identities.map((i) => (
                <li key={i.identityId} className="row-between" style={{ padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                  <span className="mono">{i.signal}</span>
                  <span>{i.value}</span>
                  <Badge variant={i.confidence === "high" ? "danger" : i.confidence === "medium" ? "warn" : "neutral"}>{i.confidence}</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Open Investigations" padded={false}>
          {cases.length === 0 ? (
            <EmptyState title="No open investigations" />
          ) : (
            <Table
              columns={[
                { key: "id", header: "Case", render: (x) => <Link to={`/investigations/${x.caseId}`} className="mono">{x.caseId}</Link> },
                { key: "risk", header: "Risk", render: (x) => <RiskBadge level={x.riskLevel} /> },
                { key: "status", header: "Status", render: (x) => <StatusBadge status={x.status} /> },
              ]}
              rows={cases}
              rowKey={(x) => x.caseId}
            />
          )}
        </Card>
      </div>

      <Card title="Knowledge Graph Relationships" padded>
        <FraudGraph data={graph} selectedId={selectedGraphNodeId} onSelect={setSelectedGraphNodeId} height={380} />
      </Card>

      <CaseMemory cases={history} title="Historical Cases" />
    </div>
  );
}