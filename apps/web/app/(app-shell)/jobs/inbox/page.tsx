import Link from "next/link";

import { importJobAction, importJobUrlAction } from "@/app/actions";
import { FeedbackBanner } from "@/components/shared/feedback-banner";
import { PageHeader } from "@/components/shared/page-header";
import { SubmitButton } from "@/components/shared/submit-button";
import { SummaryCard } from "@/components/shared/summary-card";
import { getJobsSafe } from "@/lib/api-client/jobs";

export default async function JobInboxPage({
  searchParams
}: {
  searchParams?: Promise<{ status?: string; message?: string }>;
}) {
  const feedback = (await searchParams) ?? {};
  const jobs = await getJobsSafe();
  const riskyJobs = jobs.filter((job) => job.risk_level !== "low").length;
  const topScore = jobs.length > 0 ? Math.max(...jobs.map((job) => job.score)) : 0;

  return (
    <>
      <PageHeader
        eyebrow="Jobs"
        title="A unified inbox for raw opportunities."
        description="Every source should normalize into one queue with freshness, match, and risk signals before it reaches a decision."
        meta={[
          { label: "Imported jobs", value: String(jobs.length) },
          { label: "Needs review", value: String(riskyJobs) },
          { label: "Best visible score", value: String(topScore) }
        ]}
        actions={
          <div className="button-row">
            <Link className="button" href="/resumes">
              Prepare assets
            </Link>
            <Link className="button ghost" href="/dashboard">
              Back to dashboard
            </Link>
          </div>
        }
      />
      <FeedbackBanner status={feedback.status} message={feedback.message} />
      <div className="grid three">
        <SummaryCard title="Queue size" value={String(jobs.length)} hint="All imported opportunities waiting for review." tone="accent" />
        <SummaryCard title="Review pressure" value={String(riskyJobs)} hint="Roles carrying risk flags or weak signal quality." />
        <SummaryCard title="Top visible fit" value={String(topScore)} hint="Highest current score in the inbox, useful for triage." />
      </div>
      <div className="grid two">
        <section className="card stack strong">
          <div>
            <p className="eyebrow">Import by paste</p>
            <h2>Drop raw JD text into the workspace.</h2>
            <p className="helper-copy">
              Use this when you copy a role description from a recruiter message, a job board, or an internal document.
            </p>
          </div>
          <form action={importJobAction} className="form-grid">
            <div className="form-row">
              <label className="field-label" htmlFor="raw_content">
                JD content
              </label>
              <textarea
                className="text-area"
                id="raw_content"
                name="raw_content"
                placeholder="Paste the job description here, including title, scope, and the most important requirements."
                required
              />
            </div>
            <div className="button-row">
              <SubmitButton
                label="Import From Paste"
                pendingLabel="Importing Job..."
                pendingHint="Normalizing the pasted JD and creating a new decision page."
              />
            </div>
          </form>
        </section>
        <section className="card stack">
          <div>
            <p className="eyebrow">Import by URL</p>
            <h2>Capture a role from a job link.</h2>
            <p className="helper-copy">
              Use this when you already have a canonical job post URL and want it tracked in the same inbox.
            </p>
          </div>
          <form action={importJobUrlAction} className="form-grid">
            <div className="form-row">
              <label className="field-label" htmlFor="url">
                Job URL
              </label>
              <input
                className="text-input"
                id="url"
                name="url"
                type="url"
                placeholder="https://company.example/jobs/principal-ios-platform-engineer"
                required
              />
            </div>
            <div className="button-row">
              <SubmitButton
                label="Import From URL"
                pendingLabel="Importing URL..."
                pendingHint="Creating a tracked job from the provided source URL."
                variant="secondary"
              />
            </div>
          </form>
          <div className="detail-rows">
            <div className="detail-row">
              <span>Current backend behavior</span>
              <strong>Stores the source URL and creates the job record immediately.</strong>
            </div>
          </div>
        </section>
      </div>
      <div className="grid two">
        <section className="card stack strong">
          <div className="split">
            <div>
              <p className="eyebrow">Inbox snapshot</p>
              <h2>Review roles in order of conviction</h2>
            </div>
            <span className="pill neutral">{jobs.length} visible</span>
          </div>
          {jobs.length === 0 ? (
            <div className="empty-state">
              <p className="helper-copy">
                No jobs imported yet. Use the paste or URL import controls above to create the first decision record.
              </p>
            </div>
          ) : (
            <ul className="list">
              {jobs.map((job) => (
                <li className="list-item" key={job.id}>
                  <div className="split">
                    <div>
                      <div className="list-item-title">
                        <strong>
                          <Link href={`/jobs/${job.id}`}>{job.title}</Link>
                        </strong>
                      </div>
                      <p className="muted">
                        {job.company_name} · {job.city}
                      </p>
                    </div>
                    <div className="cluster">
                      <span className="pill">Match {job.score}</span>
                      <span className={job.risk_level === "low" ? "pill neutral" : "pill warning"}>
                        Risk {job.risk_level}
                      </span>
                    </div>
                  </div>
                  <div className="button-row">
                    <Link className="button secondary" href={`/jobs/${job.id}`}>
                      Open decision page
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
        <section className="card stack">
          <div>
            <p className="eyebrow">How to work this page</p>
            <h2>Do not turn the inbox into a graveyard.</h2>
          </div>
          <div className="process-list">
            <div className="process-step">
              <span className="process-step-index">1</span>
              <strong>Triage the opportunity</strong>
              <p className="helper-copy">Look for a reasonable score, low ambiguity, and clear career upside before doing any extra work.</p>
            </div>
            <div className="process-step">
              <span className="process-step-index">2</span>
              <strong>Open the job decision center</strong>
              <p className="helper-copy">That page should be where JD evidence, fit signals, and resume actions actually come together.</p>
            </div>
            <div className="process-step">
              <span className="process-step-index">3</span>
              <strong>Create assets only when earned</strong>
              <p className="helper-copy">Use tailored versions and applications as deliberate moves, not automatic output.</p>
            </div>
          </div>
          <div className="detail-rows">
            <div className="detail-row">
              <span>Current state</span>
              <strong>Paste and URL import are now available directly in this inbox.</strong>
            </div>
            <div className="detail-row">
              <span>What works now</span>
              <strong>Import, listing, navigation, score display, and job decision flow.</strong>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
