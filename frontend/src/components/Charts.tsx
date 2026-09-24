// Small inline-SVG chart primitives. No external chart library.

interface BarDatum { label: string; value: number; color?: string; }

export function BarChart({ data, height = 180 }: { data: BarDatum[]; height?: number }) {
  const max = Math.max(1, ...data.map((d) => d.value));
  const barW = 100 / Math.max(1, data.length);
  return (
    <svg viewBox={`0 0 100 ${height}`} preserveAspectRatio="none" style={{ width: "100%", height }}>
      {data.map((d, i) => {
        const h = (d.value / max) * (height - 30);
        return (
          <g key={d.label}>
            <rect
              x={i * barW + barW * 0.15}
              y={height - 20 - h}
              width={barW * 0.7}
              height={h}
              fill={d.color ?? "var(--accent)"}
              rx={1}
            />
            <text
              x={i * barW + barW / 2}
              y={height - 6}
              fontSize="3.5"
              textAnchor="middle"
              fill="var(--text-3)"
            >
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export function LineChart({
  data,
  height = 180,
}: {
  data: { label: string; value: number }[];
  height?: number;
}) {
  const max = Math.max(1, ...data.map((d) => d.value));
  const stepX = data.length > 1 ? 100 / (data.length - 1) : 0;
  const pts = data.map((d, i) => {
    const x = i * stepX;
    const y = height - 20 - (d.value / max) * (height - 40);
    return { x, y, ...d };
  });
  const path = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");

  return (
    <svg viewBox={`0 0 100 ${height}`} preserveAspectRatio="none" style={{ width: "100%", height }}>
      <path d={path} fill="none" stroke="var(--accent)" strokeWidth="0.8" />
      {pts.map((p) => (
        <g key={p.label}>
          <circle cx={p.x} cy={p.y} r="1" fill="var(--accent)" />
          <text x={p.x} y={height - 6} fontSize="3.5" textAnchor="middle" fill="var(--text-3)">
            {p.label}
          </text>
        </g>
      ))}
    </svg>
  );
}

export function DonutChart({
  slices,
  size = 180,
}: {
  slices: { label: string; value: number; color: string }[];
  size?: number;
}) {
  const total = Math.max(1, slices.reduce((s, x) => s + x.value, 0));
  const r = 40;
  const c = 2 * Math.PI * r;
  let offset = 0;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
      <svg viewBox="0 0 100 100" width={size} height={size}>
        <g transform="translate(50 50) rotate(-90)">
          <circle r={r} fill="none" stroke="var(--border)" strokeWidth="12" />
          {slices.map((s) => {
            const len = (s.value / total) * c;
            const el = (
              <circle
                key={s.label}
                r={r}
                fill="none"
                stroke={s.color}
                strokeWidth="12"
                strokeDasharray={`${len} ${c - len}`}
                strokeDashoffset={-offset}
              />
            );
            offset += len;
            return el;
          })}
        </g>
        <text x="50" y="52" textAnchor="middle" fontSize="9" fontWeight="600" fill="var(--text)">
          {total}
        </text>
      </svg>
      <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: 12 }}>
        {slices.map((s) => (
          <li key={s.label} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
            <span style={{ width: 10, height: 10, background: s.color, borderRadius: 2, display: "inline-block" }} />
            <span style={{ color: "var(--text-2)" }}>{s.label}</span>
            <span style={{ marginLeft: "auto", color: "var(--text-3)" }}>{s.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}