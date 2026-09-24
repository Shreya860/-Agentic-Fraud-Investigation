import { useEffect, useMemo, useState } from "react";
import { dataService } from "../services/dataService";
import type { InvestigationCase } from "../types";
import Card from "../components/Card";
import { BarChart, DonutChart, LineChart } from "../components/Charts";
import { actionLabels } from "../data/mockCases";

export default function Analytics() {
  const [cases, setCases] = useState<InvestigationCase[]>([]);

  useEffect(() => {
    dataService.getInvestigations().then(setCases);
  }, []);

  const patternData = useMemo(() => {
    const counts: Record<string, number> = {};
    cases.forEach((c) => {
      const k = c.pattern ?? "Unclassified";
      counts[k] = (counts[k] ?? 0) + 1;
    });
    return Object.entries(counts).map(([label, value]) => ({ label, value }));
  }, [cases]);

  const riskDist = useMemo(() => {
    const count = (l: string) => cases.filter((c) => c.riskLevel === l).length;
    return [
      { label: "Very High", value: count("very_high"), color: "#b42318" },
      { label: "High",      value: count("high"),      color: "#b54708" },
      { label: "Moderate",  value: count("moderate"),  color: "#1d4ed8" },
      { label: "Low",       value: count("low"),       color: "#067647" },
    ];
  }, [cases]);

  const outcomes = useMemo(() => {
    const count = (s: string) => cases.filter((c) => c.status === s).length;
    return [
      { label: "Resolved",   value: count("resolved"),         color: "#067647" },
      { label: "In Flight",  value: count("investigating") + count("open"), color: "#1d4ed8" },
      { label: "Approvals",  value: count("awaiting_approval"), color: "#b54708" },
      { label: "Executed",   value: count("action_executed"),   color: "#7a5af8" },
      { label: "Closed",     value: count("closed"),            color: "#344054" },
    ];
  }, [cases]);

  const actionDist = useMemo(() => {
    const counts: Record<string, number> = {};
    cases.forEach((c) => {
      const k = actionLabels[c.nextBestAction];
      counts[k] = (counts[k] ?? 0) + 1;
    });
    return Object.entries(counts).map(([label, value]) => ({ label, value }));
  }, [cases]);

  const resolutionTrend = [
    { label: "W1", value: 4 },
    { label: "W2", value: 6 },
    { label: "W3", value: 5 },
    { label: "W4", value: 8 },
    { label: "W5", value: 11 },
    { label: "W6", value: 9 },
  ];

  const avgResolution = useMemo(() => {
    const n = cases.length;
    if (n === 0) return "0.0";
    return (n * 3.7).toFixed(1);
  }, [cases]);

  return (
    <div className="stack">
      <div className="grid grid-4">
        <div className="card stat"><div className="stat-label">Avg Resolution</div><div className="stat-value">{avgResolution}h</div></div>
        <div className="card stat"><div className="stat-label">Confirmed Fraud</div><div className="stat-value">7</div></div>
        <div className="card stat"><div className="stat-label">False Positive Rate</div><div className="stat-value">18%</div></div>
        <div className="card stat"><div className="stat-label">Total Cases</div><div className="stat-value">{cases.length}</div></div>
      </div>

      <div className="grid grid-2">
        <Card title="Fraud Patterns" subtitle="Distribution across investigations">
          <BarChart data={patternData} height={220} />
        </Card>
        <Card title="Risk Distribution">
          <DonutChart slices={riskDist} />
        </Card>
      </div>

      <div className="grid grid-2">
        <Card title="Investigation Outcomes">
          <DonutChart slices={outcomes} />
        </Card>
        <Card title="Action Distribution">
          <BarChart data={actionDist} height={220} />
        </Card>
      </div>

      <Card title="Case Resolution Trend" subtitle="Weekly resolved cases">
        <LineChart data={resolutionTrend} height={220} />
      </Card>
    </div>
  );
}