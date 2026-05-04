import type { Route } from "next";
import Link from "next/link";

import { PageHeader } from "@/components/shared/page-header";
import { SummaryCard } from "@/components/shared/summary-card";
import { getDashboardOverviewSafe } from "@/lib/api-client/dashboard";

export default async function DashboardPage() {
  const overview = await getDashboardOverviewSafe();
  const todayActions =
    overview.top_recommendations.length > 0
      ? overview.top_recommendations
      : [{ id: "fallback", title: "Import the first JD to start the workspace loop." }];
  const operatingMode = overview.ready_to_apply > 0 ? "Execute" : "Prepare";
  const actionHref = (id: string): Route => {
    if (id.startsWith("job-")) {
      return `/jobs/${id.replace("job-", "")}` as Route;
    }
    if (id.startsWith("application-")) {
      return `/applications/${id.replace("application-", "")}` as Route;
    }
    return "/jobs/inbox";
  };

  return (
    <>
      <PageHeader
        eyebrow="Today"
        title="Operate the search, not just the applications."
        description="The dashboard should surface the next best actions, active risks, and the opportunities most worth your attention."
        meta={[
          { label: "Mode", value: operatingMode },
          { label: "Action Queue", value: String(todayActions.length) },
          { label: "Upcoming Interviews", value: String(overview.interviews_upcoming) }
        ]}
        actions={
          <div className="button-row">
            <Link className="button" href="/jobs/inbox">
              Review jobs
            </Link>
            <Link className="button ghost" href="/applications/board">
              Open pipeline
            </Link>
          </div>
        }
      />
      <div className="grid three">
        <SummaryCard
          title="New jobs in 24h"
          value={String(overview.new_jobs_24h)}
          hint="Imported or refreshed opportunities in the last day."
          tone="accent"
        />
        <SummaryCard
          title="Ready to apply"
          value={String(overview.ready_to_apply)}
          hint="Applications that already have the right assets and enough conviction."
        />
        <SummaryCard
          title="Follow-ups due"
          value={String(overview.followups_due_today)}
          hint={`${overview.interviews_upcoming} interview(s) already on the horizon.`}
          tone={overview.followups_due_today > 0 ? "warning" : "default"}
        />
      </div>
      <div className="grid two">
        <section className="card strong hero-panel">
          <p className="eyebrow">Decision focus</p>
          <div className="info-grid">
            <div className="hero-metric">
              <span className="muted">Most useful next step</span>
              <div className="hero-value">{operatingMode}</div>
              <p className="helper-copy">
                {overview.ready_to_apply > 0
                  ? "You already have at least one application that can move today. Bias toward execution."
                  : "The bottleneck is still evidence and assets. Improve resume targeting before increasing volume."}
              </p>
              <div className="metric-strip">
                <span className="stat-chip">Queue {todayActions.length}</span>
                <span className="stat-chip">Ready {overview.ready_to_apply}</span>
                <span className="stat-chip">Follow-ups {overview.followups_due_today}</span>
              </div>
            </div>
            <div className="process-list">
              <div className="process-step">
                <span className="process-step-index">1</span>
                <strong>Review signal</strong>
                <p className="helper-copy">Prioritize new roles with enough upside or fresh recruiter activity.</p>
              </div>
              <div className="process-step">
                <span className="process-step-index">2</span>
                <strong>Sharpen assets</strong>
                <p className="helper-copy">Create a tailored version only when the role is worth a serious shot.</p>
              </div>
              <div className="process-step">
                <span className="process-step-index">3</span>
                <strong>Move pipeline</strong>
                <p className="helper-copy">Convert finished assets into applications and keep follow-up debt visible.</p>
              </div>
            </div>
          </div>
        </section>
        <section className="card stack">
          <div>
            <p className="eyebrow">Today&apos;s action queue</p>
            <h2>Work the highest-conviction moves first.</h2>
          </div>
          <ul className="list">
            {todayActions.map((item, index) => (
              <li className="list-item" key={item.id}>
                <div className="list-item-title">
                  <span className="process-step-index">{index + 1}</span>
                  <strong>{item.title}</strong>
                </div>
                <p className="muted">
                  {item.id.startsWith("job-")
                    ? "Open the job decision page, validate fit, and decide whether it deserves a tailored version."
                    : item.id.startsWith("application-")
                      ? "Open the application record, confirm the external state, and move the pipeline deliberately."
                    : "Seed the workspace with the next promising JD so the loop can start."}
                </p>
                <div className="button-row">
                  <Link className="button secondary" href={actionHref(item.id)}>
                    Open task
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
      <div className="grid two">
        <section className="card stack">
          <div>
            <p className="eyebrow">Operating heuristics</p>
            <h2>What the workspace is optimizing for</h2>
          </div>
          <div className="detail-rows">
            <div className="detail-row">
              <span>Decision quality</span>
              <strong>Choose roles worth customization, not just new tabs.</strong>
            </div>
            <div className="detail-row">
              <span>Asset reuse</span>
              <strong>One master resume, many deliberate variations.</strong>
            </div>
            <div className="detail-row">
              <span>Pipeline hygiene</span>
              <strong>Every application should have a stage, an owner, and a next move.</strong>
            </div>
          </div>
        </section>
        <section className="card stack">
          <div>
            <p className="eyebrow">System shape</p>
            <h2>The shell is connected to live APIs</h2>
          </div>
          <p className="helper-copy">
            When the backend is reachable, these cards read from the overview API. The fallback path keeps the workspace navigable while the local API or database is offline.
          </p>
          <div className="cluster">
            <span className="pill neutral">Live dashboard overview</span>
            <span className="pill neutral">Application-ready counts</span>
            <span className="pill neutral">Follow-up visibility</span>
          </div>
        </section>
      </div>
    </>
  );
}
