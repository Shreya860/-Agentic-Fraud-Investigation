import type { RiskAssessment, RiskLevel } from "../types";
import Badge from "./Badge";

interface Props {
  risk: RiskAssessment;
}

const levelLabel: Record<RiskLevel, string> = {
  low: "LOW",
  moderate: "MODERATE",
  high: "HIGH",
  very_high: "VERY HIGH",
};

const severityToBadge = (s: "low" | "medium" | "high" | "critical") => {
  switch (s) {
    case "critical": return "very_high";
    case "high":     return "high";
    case "medium":   return "moderate";
    default:         return "low";
  }
};

export default function RiskPanel({ risk }: Props) {
  const pct = Math.max(0, Math.min(100, risk.score));
  const barClass =
    risk.level === "very_high" || risk.level === "high"
      ? "danger"
      : risk.level === "moderate"
      ? "warn"
      : "ok";

  return (
    <section className="card">
      <header className="card-header">
        <h2>Risk Assessment</h2>
        <span className="card-title-sub">Weighted score across signals</span>
      </header>

      <div className="card-body">
        <div className="row-between mb-3">
          <div>
            <div className="section-title">Risk Level</div>
            <Badge variant={risk.level}>{levelLabel[risk.level]}</Badge>
          </div>
          <div style={{ textAlign: "right" }}>
            <div className="section-title">Risk Score</div>
            <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-0.01em" }}>
              {pct}
              <span className="muted" style={{ fontSize: 13, fontWeight: 500 }}>
                {" "}/ 100
              </span>
            </div>
          </div>
        </div>

        <div className={`score-bar ${barClass} mb-4`}>
          <span style={{ width: `${pct}%` }} />
        </div>

        <div className="section-title">Contributing Factors</div>
        <ul style={{ listStyle: "none", padding: 0, margin: "0 0 16px" }}>
          {risk.factors.map((f) => (
            <li
              key={f.id}
              style={{
                padding: "10px 0",
                borderBottom: "1px solid var(--border)",
              }}
            >
              <div className="row-between">
                <div style={{ fontWeight: 600, fontSize: 13 }}>{f.label}</div>
                <Badge variant={severityToBadge(f.severity)}>
                  {f.severity.toUpperCase()}
                </Badge>
              </div>
              <div className="small muted mt-1">{f.description}</div>
              <div className="evidence-meta mt-1">
                <span>Confidence: {f.confidence}</span>
              </div>
            </li>
          ))}
        </ul>

        <div className="section-title">Assessment</div>
        <p style={{ margin: 0, fontSize: 13, color: "var(--text-2)", lineHeight: 1.6 }}>
          {risk.summary}
        </p>
      </div>
    </section>
  );
}