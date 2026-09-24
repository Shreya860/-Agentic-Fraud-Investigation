import type { TimelineEvent } from "../types";

interface Props {
  events: TimelineEvent[];
}

export default function InvestigationTimeline({ events }: Props) {
  return (
    <ol className="timeline">
      {events.map((e) => (
        <li key={e.id} className={e.status}>
          <span className="dot" />
          <div className="t-label">
            {e.step}. {e.label}
          </div>
          {e.timestamp && (
            <div className="t-meta">
              {new Date(e.timestamp).toLocaleString()}
            </div>
          )}
        </li>
      ))}
    </ol>
  );
}