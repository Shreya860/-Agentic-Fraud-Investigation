import { FileText, Download } from "lucide-react";
import Card from "../components/Card";
import { useApp } from "../context/AppContext";

const reports = [
  { id: "RPT-1", title: "Investigation Summary",  description: "Summary of all open and recently resolved investigations." },
  { id: "RPT-2", title: "Fraud Pattern Report",   description: "Distribution of fraud patterns across cases." },
  { id: "RPT-3", title: "Risk Exposure Report",   description: "Exposure by risk level, customer and merchant." },
  { id: "RPT-4", title: "Analyst Activity Report",description: "Cases handled, actions executed, avg resolution time." },
];

export default function Reports() {
  const { pushToast } = useApp();

  const stub = (what: string) =>
    pushToast(`${what} will be connected to the backend later.`, "info");

  return (
    <div className="stack">
      <div className="grid grid-2">
        {reports.map((r) => (
          <Card
            key={r.id}
            title={r.title}
            right={<span className="badge badge-neutral">PDF · CSV</span>}
          >
            <div className="row" style={{ gap: 10, alignItems: "flex-start" }}>
              <FileText size={20} color="var(--text-3)" />
              <div style={{ flex: 1 }}>
                <div className="small muted">{r.description}</div>
                <div className="row mt-3" style={{ gap: 8 }}>
                  <button className="btn btn-sm" onClick={() => stub(`View for "${r.title}"`)}>
                    View Report
                  </button>
                  <button className="btn btn-sm" onClick={() => stub(`PDF export for "${r.title}"`)}>
                    <Download size={13} /> Export PDF
                  </button>
                  <button className="btn btn-sm" onClick={() => stub(`CSV export for "${r.title}"`)}>
                    <Download size={13} /> Export CSV
                  </button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Card title="Scheduled Reports">
        <table className="tbl">
          <thead>
            <tr>
              <th>Report</th>
              <th>Schedule</th>
              <th>Recipients</th>
              <th>Last Run</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>Investigation Summary</td><td>Daily 07:00</td><td>fraud-ops@…</td><td>2024-06-11</td></tr>
            <tr><td>Risk Exposure Report</td><td>Weekly Mon</td><td>risk-committee@…</td><td>2024-06-10</td></tr>
            <tr><td>Analyst Activity Report</td><td>Monthly</td><td>analytics@…</td><td>2024-06-01</td></tr>
          </tbody>
        </table>
      </Card>
    </div>
  );
}