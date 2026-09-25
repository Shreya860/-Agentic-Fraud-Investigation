import { useEffect, useMemo, useState } from "react";
import { dataService, type AnalyticsData } from "../services/dataService";
import type { ActionType } from "../types";
import Card from "../components/Card";
import { BarChart, DonutChart, LineChart } from "../components/Charts";
import { actionLabels } from "../data/mockCases";

export default function Analytics() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);

  useEffect(() => {
    dataService.getAnalytics().then(setAnalytics);
  }, []);

  const patternData = useMemo(() => {
    return Object.entries(analytics?.casesPerTriggerType ?? {}).map(([label, value]) => ({ label, value }));
  }, [analytics]);

  const riskDist = useMemo(() => {
    return [
      { label: "Very High", value: analytics?.riskDistribution.very_high ?? 0, color: "#b42318" },
      { label: "High",      value: analytics?.riskDistribution.high ?? 0,      color: "#b54708" },
      { label: "Moderate",  value: analytics?.riskDistribution.moderate ?? 0,  color: "#1d4ed8" },
      { label: "Low",       value: analytics?.riskDistribution.low ?? 0,       color: "#067647" },
    ];
  }, [analytics]);

  const customerData = useMemo(
    () => Object.entries(analytics?.casesPerCustomer ?? {}).map(([label, value], index) => ({
      label,
      value,
      color: ["#1d4ed8", "#067647", "#b54708", "#7a5af8", "#b42318"][index % 5],
    })),
    [analytics]
  );

  const actionDist = useMemo(() => {
    return Object.entries(analytics?.recommendedActionDistribution ?? {}).map(([action, value]) => ({
      label: actionLabels[action as ActionType] ?? action,
      value: value ?? 0,
    }));
  }, [analytics]);

  return (
    <div className="stack">
      <div className="grid grid-4">
        <div className="card stat"><div className="stat-label">Average Risk Score</div><div className="stat-value">{((analytics?.averageRiskScore ?? 0) * 100).toFixed(0)}</div></div>
        <div className="card stat"><div className="stat-label">Customers With Cases</div><div className="stat-value">{Object.keys(analytics?.casesPerCustomer ?? {}).length}</div></div>
        <div className="card stat"><div className="stat-label">Trigger Types</div><div className="stat-value">{Object.keys(analytics?.casesPerTriggerType ?? {}).length}</div></div>
        <div className="card stat"><div className="stat-label">Total Cases</div><div className="stat-value">{analytics?.totalCases ?? 0}</div></div>
      </div>

      <div className="grid grid-2">
        <Card title="Cases per Trigger Type" subtitle="Distribution across benchmark investigations">
          <BarChart data={patternData} height={220} />
        </Card>
        <Card title="Risk Distribution">
          <DonutChart slices={riskDist} />
        </Card>
      </div>

      <div className="grid grid-2">
        <Card title="Cases per Customer">
        <DonutChart slices={customerData.slice(0, 8)} />
        </Card>
        <Card title="Action Distribution">
          <BarChart data={actionDist} height={220} />
        </Card>
      </div>

      <Card title="Cases per Trigger Type" subtitle="Benchmark trigger distribution">
        <LineChart data={patternData} height={220} />
      </Card>
    </div>
  );
}