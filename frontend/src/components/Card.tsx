import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  subtitle?: string;
  right?: ReactNode;
  children: ReactNode;
  padded?: boolean;
}

export default function Card({ title, subtitle, right, children, padded = true }: CardProps) {
  return (
    <section className="card">
      {(title || right) && (
        <header className="card-header">
          <h2>{title}</h2>
          {subtitle && <span className="card-title-sub">{subtitle}</span>}
          {right && <div style={{ marginLeft: "auto" }}>{right}</div>}
        </header>
      )}
      <div className={padded ? "card-body" : ""}>{children}</div>
    </section>
  );
}