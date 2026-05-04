import { ReactNode } from "react";

type SummaryCardProps = {
  title: string;
  value: string;
  hint: string;
  aside?: ReactNode;
  tone?: "default" | "accent" | "warning";
};

export function SummaryCard({ title, value, hint, aside, tone = "default" }: SummaryCardProps) {
  return (
    <section className={`card summary-card tone-${tone}`}>
      <div className="split summary-card-head">
        <div className="summary-card-copy">
          <p className="eyebrow">{title}</p>
          <h2 className="summary-card-value">{value}</h2>
          <p className="muted">{hint}</p>
        </div>
        {aside ? <div className="summary-card-aside">{aside}</div> : null}
      </div>
    </section>
  );
}
