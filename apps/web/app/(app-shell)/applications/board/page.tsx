import Link from "next/link";

import { PageHeader } from "@/components/shared/page-header";
import { SummaryCard } from "@/components/shared/summary-card";
import { getApplicationsSafe } from "@/lib/api-client/applications";

const stages = ["draft", "ready_to_apply", "applied", "hr_replied", "interview"];

export default async function ApplicationBoardPage() {
  const applications = await getApplicationsSafe();
  const readyCount = applications.filter((application) => application.current_stage === "ready_to_apply").length;
  const appliedCount = applications.filter((application) => application.current_stage === "applied").length;
  const activeCount = applications.filter((application) => application.current_stage !== "draft").length;

  const formatStageLabel = (stage: string) =>
    stage
      .split("_")
      .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
      .join(" ");

  return (
    <>
      <PageHeader
        eyebrow="Applications"
        title="Track movement, not just volume."
        description="The board should make follow-ups, transitions, and conversion quality visible without turning the search into noisy vanity metrics."
        meta={[
          { label: "Total applications", value: String(applications.length) },
          { label: "Ready to apply", value: String(readyCount) },
          { label: "Active pipeline", value: String(activeCount) }
        ]}
        actions={
          <div className="button-row">
            <Link className="button" href="/jobs/inbox">
              Review jobs
            </Link>
            <Link className="button ghost" href="/dashboard">
              Open dashboard
            </Link>
          </div>
        }
      />
      <div className="grid three">
        <SummaryCard title="Pipeline size" value={String(applications.length)} hint="All tracked applications across the visible stages." tone="accent" />
        <SummaryCard title="Ready to apply" value={String(readyCount)} hint="Applications with enough context and assets to move now." />
        <SummaryCard title="Applied or later" value={String(appliedCount)} hint="Applications that already crossed into external execution." />
      </div>
      <section className="card stack">
        <div className="split">
          <div>
            <p className="eyebrow">Pipeline board</p>
            <h2>Keep momentum visible.</h2>
          </div>
          <span className="pill neutral">{applications.length} tracked</span>
        </div>
        <div className="kanban-grid">
          {stages.map((stage) => {
            const items = applications.filter((application) => application.current_stage === stage);

            return (
              <section className="kanban-column" key={stage}>
                <div className="kanban-column-header">
                  <h3 className="kanban-column-title">{formatStageLabel(stage)}</h3>
                  <span className="pill">{items.length}</span>
                </div>
                {items.length === 0 ? (
                  <div className="empty-state">
                    <p className="helper-copy">No applications in this stage.</p>
                  </div>
                ) : (
                  <ul className="list">
                    {items.map((application) => (
                      <li className="list-item" key={application.id}>
                        <div className="list-item-title">
                          <strong>
                            <Link href={`/applications/${application.id}`}>{application.job_title}</Link>
                          </strong>
                        </div>
                        <p className="muted">{application.company_name}</p>
                        <div className="button-row">
                          <Link className="button secondary" href={`/applications/${application.id}`}>
                            Open detail
                          </Link>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            );
          })}
        </div>
      </section>
    </>
  );
}
