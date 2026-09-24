import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { dataService } from "../services/dataService";
import type {
  Transaction,
  Card as CardT,
  Device,
  Identity,
  InvestigationCase,
  GraphData,
} from "../types";
import Card from "../components/Card";
import Badge, { RiskBadge, StatusBadge } from "../components/Badge";
import EmptyState from "../components/EmptyState";
import FraudGraph from "../components/FraudGraph";
import { useApp } from "../context/AppContext";

export default function TransactionDetails() {
  const { transactionId = "" } = useParams<{ transactionId: string }>();
  const { selectedGraphNodeId, setSelectedGraphNodeId } = useApp();

  const [t, setT] = useState<Transaction | null | undefined>(undefined);
  const [card, setCard] = useState<CardT | null>(null);
  const [device, setDevice] = useState<Device | null>(null);
  const [identities, setIdentities] = useState<Identity[]>([]);
  const [related, setRelated] = useState<Transaction[]>([]);
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [graph, setGraph] = useState<GraphData>({ nodes: [], edges: [] });

  useEffect(() => {
    let alive = true;
    Promise.all([
      dataService.getTransaction(transactionId),
      dataService.getCards(),
      dataService.getDevices(),
      dataService.getIdentities(),
      dataService.getTransactions(),
      dataService.getInvestigations(),
      dataService.getGraphData("CASE-48291"),
    ]).then(([tx, cd, dv, id, all, cs, gr]) => {
      if (!alive) return;
      setT(tx ?? null);
      if (tx) {
        setCard(cd.find((x) => x.cardId === tx.cardId) ?? null);
        setDevice(dv.find((x) => x.deviceId === tx.deviceId) ?? null);
        setIdentities(id.filter((x) => x.customerId === tx.customerId));
        setRelated(all.filter((x) => x.customerId === tx.customerId && x.transactionId !== tx.transactionId));
        setCases(cs.filter((c) => c.flaggedTransactionId === tx.transactionId));
      }
      setGraph(gr);
    });
    return () => {
      alive = false;
    };
  }, [transactionId]);

  if (t === undefined) return <div className="muted">Loading transaction…</div>;
  if (t === null) return <EmptyState title="Transaction not found" subtitle={`No transaction with id ${transactionId}`} />;

  return (
    <div className="stack">
      <div className="card" style={{ padding: 16 }}>
        <div className="row-between">
          <div>
            <h1 className="mono" style={{ fontSize: 18 }}>{t.transactionId}</h1>
            <div className="small muted mt-1">
              {t.channel} · {t.merchant} · {t.location} · {new Date(t.timestamp).toLocaleString()}
            </div>
          </div>
          <RiskBadge level={t.riskLevel} score={t.riskScore} />
        </div>
      </div>

      <div className="grid grid-4">
        <div className="card stat"><div className="stat-label">Amount</div><div className="stat-value">${t.amount.toFixed(2)}</div></div>
        <div className="card stat"><div className="stat-label">Risk Score</div><div className="stat-value">{(t.riskScore * 100).toFixed(0)}</div></div>
        <div className="card stat"><div className="stat-label">Status</div><div className="stat-value" style={{ fontSize: 16 }}>{t.status}</div></div>
        <div className="card stat"><div className="stat-label">Channel</div><div className="stat-value" style={{ fontSize: 16 }}>{t.channel}</div></div>
      </div>

      <Card title="Transaction Information">
        <dl className="kv">
          <dt>Transaction ID</dt><dd className="mono">{t.transactionId}</dd>
          <dt>Customer</dt><dd><Link to={`/customers/${t.customerId}`}>{t.customerName}</Link></dd>
          <dt>Amount</dt><dd>${t.amount.toFixed(2)} {t.currency}</dd>
          <dt>Channel</dt><dd>{t.channel}</dd>
          <dt>Merchant</dt><dd>{t.merchant}</dd>
          <dt>Location</dt><dd>{t.location}</dd>
          <dt>Timestamp</dt><dd>{new Date(t.timestamp).toLocaleString()}</dd>
        </dl>
      </Card>

      <div className="grid grid-2">
        <Card title="Card">
          {card ? (
            <dl className="kv">
              <dt>Card</dt><dd className="mono">•••• {card.last4}</dd>
              <dt>Network</dt><dd>{card.network}</dd>
              <dt>Type</dt><dd>{card.type}</dd>
              <dt>Status</dt><dd>{card.status}</dd>
            </dl>
          ) : (
            <EmptyState title="No card linked" />
          )}
        </Card>

        <Card title="Device">
          {device ? (
            <dl className="kv">
              <dt>Device</dt><dd className="mono">{device.deviceId}</dd>
              <dt>OS</dt><dd>{device.os}</dd>
              <dt>Fingerprint</dt><dd className="mono">{device.fingerprint}</dd>
              <dt>Linked Customers</dt>
              <dd>
                <Badge variant={device.linkedCustomers > 1 ? "danger" : "neutral"}>
                  {device.linkedCustomers}
                </Badge>
              </dd>
            </dl>
          ) : (
            <EmptyState title="No device linked" />
          )}
        </Card>
      </div>

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

      <Card title="Risk Signals">
        <ul style={{ paddingLeft: 18 }}>
          <li>Amount is ${t.amount.toFixed(2)} — flagged as {t.riskLevel.replace(/_/g, " ")} risk.</li>
          <li>Merchant: {t.merchant} ({t.location}).</li>
          <li>Channel: {t.channel}.</li>
          {device && device.linkedCustomers > 1 && (
            <li>Device {device.deviceId} is linked to {device.linkedCustomers} customer accounts.</li>
          )}
        </ul>
      </Card>

      <div className="grid grid-2">
        <Card title="Related Transactions" padded={false}>
          {related.length === 0 ? (
            <EmptyState title="No related transactions" />
          ) : (
            <table className="tbl">
              <thead>
                <tr>
                  <th>Transaction</th>
                  <th>Amount</th>
                  <th>Channel</th>
                  <th>Risk</th>
                </tr>
              </thead>
              <tbody>
                {related.slice(0, 8).map((r) => (
                  <tr key={r.transactionId}>
                    <td><Link to={`/transactions/${r.transactionId}`} className="mono">{r.transactionId}</Link></td>
                    <td className="num">${r.amount.toFixed(2)}</td>
                    <td>{r.channel}</td>
                    <td><RiskBadge level={r.riskLevel} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>

        <Card title="Related Cases" padded={false}>
          {cases.length === 0 ? (
            <EmptyState title="No related cases" />
          ) : (
            <table className="tbl">
              <thead>
                <tr>
                  <th>Case</th>
                  <th>Status</th>
                  <th>Risk</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr key={c.caseId}>
                    <td><Link to={`/investigations/${c.caseId}`} className="mono">{c.caseId}</Link></td>
                    <td><StatusBadge status={c.status} /></td>
                    <td><RiskBadge level={c.riskLevel} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>
      </div>

      <Card title="Graph Relationships" padded>
        <FraudGraph
          data={graph}
          selectedId={selectedGraphNodeId}
          onSelect={setSelectedGraphNodeId}
          height={380}
        />
      </Card>
    </div>
  );
}