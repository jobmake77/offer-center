import Link from "next/link";

import { uploadResumeAction } from "@/app/actions";
import { FeedbackBanner } from "@/components/shared/feedback-banner";
import { PageHeader } from "@/components/shared/page-header";
import { SubmitButton } from "@/components/shared/submit-button";
import { SummaryCard } from "@/components/shared/summary-card";
import { getResumesSafe } from "@/lib/api-client/resumes";

export default async function ResumesPage({
  searchParams
}: {
  searchParams?: Promise<{ status?: string; message?: string }>;
}) {
  const feedback = (await searchParams) ?? {};
  const resumes = await getResumesSafe();
  const masterResumeCount = resumes.filter((resume) => resume.is_master).length;
  const parsedResumeCount = resumes.filter((resume) => resume.parser_status === "succeeded").length;

  return (
    <>
      <PageHeader
        eyebrow="Resume Assets"
        title="Manage the master resume and every targeted variation."
        description="The system should store a canonical source resume, reusable bullets, and job-specific versions instead of treating each PDF as disposable."
        meta={[
          { label: "Imported resumes", value: String(resumes.length) },
          { label: "Master resumes", value: String(masterResumeCount) },
          { label: "Ready assets", value: String(parsedResumeCount) }
        ]}
        actions={
          <div className="button-row">
            <Link className="button" href="/jobs/inbox">
              Go to jobs
            </Link>
            <Link className="button ghost" href="/dashboard">
              Open dashboard
            </Link>
          </div>
        }
      />
      <FeedbackBanner status={feedback.status} message={feedback.message} />
      <div className="grid three">
        <SummaryCard title="Resume library" value={String(resumes.length)} hint="Every source resume or base asset currently stored." tone="accent" />
        <SummaryCard title="Canonical sources" value={String(masterResumeCount)} hint="Resumes marked as the stable baseline for derivative versions." />
        <SummaryCard title="Parser-ready" value={String(parsedResumeCount)} hint="Assets that already completed parsing and can be reused." />
      </div>
      <div className="grid two">
        <section className="card stack strong">
          <div className="split">
            <div>
              <p className="eyebrow">Imported resumes</p>
              <h2>Keep the source of truth clean.</h2>
            </div>
            <span className="pill neutral">{resumes.length} stored</span>
          </div>
          {resumes.length === 0 ? (
            <div className="empty-state">
              <p className="helper-copy">No resumes uploaded yet. The first upload becomes the seed for every tailored version you create later.</p>
            </div>
          ) : (
            <ul className="list">
              {resumes.map((resume) => (
                <li className="list-item" key={resume.id}>
                  <div className="split">
                    <div>
                      <div className="list-item-title">
                        <strong>{resume.name}</strong>
                      </div>
                      <p className="muted">Parser status: {resume.parser_status}</p>
                    </div>
                    <div className="cluster">
                      {resume.is_master ? <span className="pill">Master</span> : null}
                      <span className="pill neutral">{resume.parser_status}</span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
        <section className="card stack">
          <div>
            <p className="eyebrow">Upload a new resume</p>
            <h2>Add a reusable foundation, not a throwaway file.</h2>
            <p className="helper-copy">
              This upload should enrich the long-lived profile. Later job-specific versions should branch off this source, not replace it.
            </p>
          </div>
          <form action={uploadResumeAction} className="form-grid">
            <div className="form-row">
              <label className="field-label" htmlFor="resume_file">
                Resume file
              </label>
              <input className="file-input" id="resume_file" name="resume_file" type="file" required />
            </div>
            <div className="button-row">
              <SubmitButton
                label="Upload Resume"
                pendingLabel="Uploading Resume..."
                pendingHint="Storing the source resume and kicking off parsing."
              />
              <Link className="button secondary" href="/jobs/inbox">
                Open jobs inbox
              </Link>
            </div>
          </form>
          <div className="detail-rows">
            <div className="detail-row">
              <span>Best use</span>
              <strong>Store the highest-signal baseline version of your experience.</strong>
            </div>
            <div className="detail-row">
              <span>Then do this</span>
              <strong>Open a target job and create a tailored version from that baseline.</strong>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
