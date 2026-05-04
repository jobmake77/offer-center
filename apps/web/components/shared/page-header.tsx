import { ReactNode } from "react";

type PageHeaderProps = {
  title: string;
  description: string;
  eyebrow?: string;
  meta?: Array<{ label: string; value: string }>;
  actions?: ReactNode;
};

export function PageHeader({ title, description, eyebrow, meta = [], actions }: PageHeaderProps) {
  return (
    <header className="page-header">
      <div className="page-header-shell">
        <div className="page-header-copy">
          {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
          <h1>{title}</h1>
          <p>{description}</p>
          {meta.length > 0 ? (
            <div className="page-meta-row">
              {meta.map((item) => (
                <div className="page-meta-pill" key={`${item.label}-${item.value}`}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          ) : null}
        </div>
        {actions ? <div className="page-header-actions">{actions}</div> : null}
      </div>
    </header>
  );
}
