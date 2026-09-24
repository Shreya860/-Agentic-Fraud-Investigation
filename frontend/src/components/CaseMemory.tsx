import type { HistoricalCase } from "../types";
import Badge from "./Badge";

interface Props {
  cases: HistoricalCase[];
  title?: string;
}

function outcomeVariant(o: HistoricalCase["outcome"]) {
  switch (o) {
    case "confirmed_fraud": return "danger";
    case "false_positive":  return "ok";
    default:                return "neutral";
  }
}

const outcomeLabel: Record<HistoricalCase["outcome"], string> = {
  confirmed_fraud: "Confirmed Fraud",
  false_positive:  "False Positive",
  inconclusive:    "Inconclusive",
};

export default function CaseMemory({ cases, title = "Historical Similar Cases" }: Props) {
  return (
    <section className="card">
      <header className="card-header">
        <h2>{title}</h2>
        <span className="card-title-sub">{cases.length} matches</span>
      </header>

      <div className="card-body">
        {cases.length === 0 ? (
          <div className="muted small">No historical cases found.</div>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {cases.map((c) => (
              <li
                key={c.caseId}
                style={{ padding: "10px 0", borderBottom: "1px solid var(--border)" }}
              >
                <div className="row-between">
                  <div className="row" style={{ gap: 10 }}>
                    <span className="mono" style={{ fontWeight: 600 }}>{c.caseId}</span>
                    <span className="small muted">{c.pattern}</span>
                  </div>
                  <div className="row" style={{ gap: 6 }}>
                    <Badge variant={outcomeVariant(c.outcome)}>
                      {outcomeLabel[c.outcome]}
                    </Badge>
                    <Badge variant="neutral">
                      {(c.similarity * 100).toFixed(0)}%
                    </Badge>
                  </div>
                </div>
                <div className="small muted mt-1">{c.summary}</div>
                <div className="evidence-meta mt-1">
                  <span>Customer: {c.customerName}</span>
                  <span>{c.date}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}