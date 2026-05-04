import Link from "next/link";

import {
  createApplicationAction,
  createResumeVersionAction,
  generateMatchReportAction
} from "@/app/actions";
import { FeedbackBanner } from "@/components/shared/feedback-banner";
import { getJobSafe, getMatchReportsSafe } from "@/lib/api-client/jobs";
import { getResumesSafe, getResumeVersionsSafe } from "@/lib/api-client/resumes";
import { PageHeader } from "@/components/shared/page-header";
import { SubmitButton } from "@/components/shared/submit-button";
import { SummaryCard } from "@/components/shared/summary-card";

export default async function JobDetailPage({
  params,
  searchParams
}: {
  params: Promise<{ jobId: string }>;
  searchParams?: Promise<{ status?: string; message?: string }>;
}) {
  const { jobId } = await params;
  const feedback = (await searchParams) ?? {};
  const [job, reports, resumes, resumeVersions] = await Promise.all([
    getJobSafe(jobId),
    getMatchReportsSafe(jobId),
    getResumesSafe(),
    getResumeVersionsSafe({ jobPostingId: jobId })
  ]);
  const latestReport = reports[0] ?? job.latest_match_report_summary;
  const latestOverallScore = latestReport ? String(Math.round(latestReport.scores.overall)) : "Pending";
  const applicationSummary = job.current_application_summary;
  const workflowState =
    applicationSummary
      ? "In pipeline"
      : latestReport
        ? "Ready to apply"
        : resumeVersions.length > 0
          ? "Ready to score"
          : resumes.length > 0
            ? "Needs tailored version"
            : "Needs source resume";

  return (
    <>
      <PageHeader
        eyebrow="Job Detail"
        title={`Decision center for ${job.title}`}
        description="This page should combine structured JD output, match evidence, company signals, and the next recommended action."
        meta={[
          { label: "Decision state", value: workflowState },
          { label: "Resume sources", value: String(resumes.length) },
          { label: "Linked versions", value: String(resumeVersions.length) }
        ]}
        actions={
          <div className="button-row">
            <Link className="button" href="/jobs/inbox">
              Back to inbox
            </Link>
            <Link className="button ghost" href={`/jobs/${jobId}/analysis`}>
              Deep analysis
            </Link>
          </div>
        }
      />
      <FeedbackBanner status={feedback.status} message={feedback.message} />
      <div className="grid three">
        <SummaryCard title="Latest fit score" value={latestOverallScore} hint="The most recent match score generated for this role." tone="accent" />
        <SummaryCard title="Source resumes" value={String(resumes.length)} hint="Baseline resumes that can still be tailored for this opportunity." />
        <SummaryCard
          title="Pipeline state"
          value={applicationSummary ? applicationSummary.current_stage : String(resumeVersions.length)}
          hint={applicationSummary ? "This role already has an application record." : "Targeted versions already prepared for this role."}
        />
      </div>
      <div className="grid two">
        <section className="card strong hero-panel stack">
          <div>
            <p className="eyebrow">Recommendation</p>
            <h2>Decide whether this role deserves a real swing.</h2>
          </div>
          <div className="info-grid">
            <div className="hero-metric">
              <span className="muted">Current status</span>
              <div className="hero-value">{latestOverallScore}</div>
              <p className="helper-copy">
                {latestReport
                  ? `Latest overall score: ${latestReport.scores.overall}. Use the fit evidence and tailored suggestions below before sending an application.`
                  : "No match report has been generated yet. First create a job-linked resume version, then score the role."}
              </p>
              <div className="metric-strip">
                <span className="stat-chip">{workflowState}</span>
                <span className="stat-chip">{reports.length} report(s)</span>
              </div>
            </div>
            <div className="process-list">
              <div className="process-step">
                <span className="process-step-index">1</span>
                <strong>Create the targeted asset</strong>
                <p className="helper-copy">Branch from a trusted source resume and make the job scope explicit.</p>
              </div>
              <div className="process-step">
                <span className="process-step-index">2</span>
                <strong>Generate the fit signal</strong>
                <p className="helper-copy">Use the match report to decide whether this role is merely interesting or actually worth applying to.</p>
              </div>
              <div className="process-step">
                <span className="process-step-index">3</span>
                <strong>Create the application record</strong>
                <p className="helper-copy">Only move the role into the pipeline once the asset and conviction both exist.</p>
              </div>
            </div>
          </div>
        </section>
        <section className="card stack">
          <div>
            <p className="eyebrow">Evidence blocks</p>
            <h2>What the system currently knows</h2>
          </div>
          {latestReport ? (
            <div className="stack">
              <div className="detail-rows">
                <div className="detail-row">
                  <span>Strengths</span>
                  <strong>{latestReport.strengths.length}</strong>
                </div>
                <div className="detail-row">
                  <span>Missing requirements</span>
                  <strong>{latestReport.missing_requirements.length}</strong>
                </div>
                <div className="detail-row">
                  <span>Suggestions</span>
                  <strong>{latestReport.tailored_suggestions.length}</strong>
                </div>
              </div>
              <ul className="list">
                {latestReport.strengths.map((item, index) => (
                  <li className="list-item" key={`strength-${index}-${item}`}>
                    {item}
                  </li>
                ))}
                {latestReport.tailored_suggestions.map((item, index) => (
                  <li className="list-item" key={`suggestion-${index}-${item}`}>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <pre className="code-block">{JSON.stringify(job.structured_jd, null, 2)}</pre>
          )}
        </section>
      </div>
      <div className="grid two">
        <section className="card stack strong">
          <div>
            <p className="eyebrow">Step 1</p>
            <h2>Create resume version</h2>
            <p className="helper-copy">Pick one imported resume and create a job-linked tailored version.</p>
          </div>
          {resumes.length === 0 ? (
            <div className="empty-state">
              <p className="helper-copy">
                No resumes are available yet. <Link href="/resumes">Upload one first.</Link>
              </p>
            </div>
          ) : (
            <form action={createResumeVersionAction} className="form-grid">
              <input type="hidden" name="job_id" value={jobId} />
              <div className="form-row">
                <label className="field-label" htmlFor="resume_id">
                  Source resume
                </label>
                <select className="select-input" id="resume_id" name="resume_id" required defaultValue={resumes[0]?.id}>
                  {resumes.map((resume) => (
                    <option key={resume.id} value={resume.id}>
                      {resume.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-row">
                <label className="field-label" htmlFor="instructions">
                  Tailoring instructions
                </label>
                <textarea
                  className="text-area"
                  id="instructions"
                  name="instructions"
                  placeholder="Emphasize architecture ownership, platform scope, and cross-team leadership."
                />
              </div>
              <div className="button-row">
                <SubmitButton
                  label="Create Version"
                  pendingLabel="Creating Version..."
                  pendingHint="Generating a job-linked resume variant and preparing the editor page."
                />
              </div>
            </form>
          )}
        </section>
        <section className="card stack">
          <div>
            <p className="eyebrow">Step 2 and 3</p>
            <h2>Generate match and create application</h2>
            <p className="helper-copy">Use an existing job-linked version to score the role, then optionally create the application record.</p>
          </div>
          {resumeVersions.length === 0 ? (
            <div className="empty-state">
              <p className="helper-copy">No job-linked resume versions exist yet. Create one first from the left panel.</p>
            </div>
          ) : applicationSummary ? (
            <div className="empty-state">
              <p className="helper-copy">
                This role is already tracked in the application pipeline at stage {applicationSummary.current_stage}.
              </p>
              <div className="button-row">
                <Link className="button secondary" href={`/applications/${applicationSummary.id}`}>
                  Open application
                </Link>
                <Link className="button ghost" href="/applications/board">
                  View board
                </Link>
              </div>
            </div>
          ) : (
            <>
              <form action={generateMatchReportAction} className="form-grid">
                <input type="hidden" name="job_id" value={jobId} />
                <div className="form-row">
                  <label className="field-label" htmlFor="resume_version_id">
                    Resume version
                  </label>
                  <select
                    className="select-input"
                    id="resume_version_id"
                    name="resume_version_id"
                    required
                    defaultValue={resumeVersions[0]?.id}
                  >
                    {resumeVersions.map((version) => (
                      <option key={version.id} value={version.id}>
                        {version.version_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="button-row">
                  <SubmitButton
                    label="Generate Match Report"
                    pendingLabel="Generating Match..."
                    pendingHint="Scoring fit, collecting evidence, and refreshing this job view."
                  />
                </div>
              </form>
              <form action={createApplicationAction} className="form-grid">
                <input type="hidden" name="job_id" value={jobId} />
                <div className="form-row">
                  <label className="field-label" htmlFor="application_resume_version_id">
                    Resume version
                  </label>
                  <select
                    className="select-input"
                    id="application_resume_version_id"
                    name="resume_version_id"
                    required
                    defaultValue={resumeVersions[0]?.id}
                  >
                    {resumeVersions.map((version) => (
                      <option key={version.id} value={version.id}>
                        {version.version_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-row">
                  <label className="field-label" htmlFor="source_channel">
                    Source channel
                  </label>
                  <select className="select-input" id="source_channel" name="source_channel" defaultValue="manual">
                    <option value="manual">manual</option>
                    <option value="company_site">company_site</option>
                    <option value="email">email</option>
                  </select>
                </div>
                <div className="button-row">
                  <SubmitButton
                    label="Create Application"
                    pendingLabel="Creating Application..."
                    pendingHint="Opening an application record and linking it to this job and resume version."
                    variant="secondary"
                  />
                </div>
              </form>
            </>
          )}
        </section>
      </div>
      <section className="card stack">
        <div className="split">
          <div>
            <p className="eyebrow">Structured JD</p>
            <h2>Normalized job data snapshot</h2>
          </div>
          <span className="pill neutral">{job.id.slice(0, 8)}</span>
        </div>
        <pre className="code-block">{JSON.stringify(job.structured_jd, null, 2)}</pre>
      </section>
    </>
  );
}
