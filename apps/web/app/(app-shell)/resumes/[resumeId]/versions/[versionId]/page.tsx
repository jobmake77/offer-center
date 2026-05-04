import Link from "next/link";

import { FeedbackBanner } from "@/components/shared/feedback-banner";
import { getResumeVersionSafe } from "@/lib/api-client/resumes";
import { PageHeader } from "@/components/shared/page-header";
import { SummaryCard } from "@/components/shared/summary-card";

export default async function ResumeVersionEditorPage({
  params,
  searchParams
}: {
  params: Promise<{ resumeId: string; versionId: string }>;
  searchParams?: Promise<{ status?: string; message?: string }>;
}) {
  const { resumeId, versionId } = await params;
  const feedback = (await searchParams) ?? {};
  const version = await getResumeVersionSafe(versionId);

  return (
    <>
      <PageHeader
        eyebrow="Resume Editor"
        title={`Resume ${resumeId}, version ${version.version_name}`}
        description="The editor should place JD requirements and resume bullets side by side so the user can adjust the version without losing structure."
        meta={[
          { label: "Version type", value: version.version_type },
          { label: "Status", value: version.generation_status },
          { label: "Linked job", value: version.job_posting_id ? version.job_posting_id.slice(0, 8) : "Not linked" }
        ]}
        actions={
          <div className="button-row">
            <Link className="button" href={version.job_posting_id ? `/jobs/${version.job_posting_id}` : "/resumes"}>
              {version.job_posting_id ? "Back to job" : "Back to resumes"}
            </Link>
          </div>
        }
      />
      <FeedbackBanner status={feedback.status} message={feedback.message} />
      <div className="grid three">
        <SummaryCard title="Version type" value={version.version_type} hint="How this variant was created and intended to be used." tone="accent" />
        <SummaryCard title="Generation status" value={version.generation_status} hint="Whether this version is currently available for the next action." />
        <SummaryCard
          title="Linked role"
          value={version.job_posting_id ? version.job_posting_id.slice(0, 8) : "None"}
          hint="The target job this version was created for."
        />
      </div>
      <div className="grid two">
        <section className="card stack">
          <div>
            <p className="eyebrow">Version metadata</p>
            <h2>Editing context</h2>
          </div>
          <div className="detail-rows">
            <div className="detail-row">
              <span>Type</span>
              <strong>{version.version_type}</strong>
            </div>
            <div className="detail-row">
              <span>Status</span>
              <strong>{version.generation_status}</strong>
            </div>
            <div className="detail-row">
              <span>Linked job</span>
              <strong>{version.job_posting_id ?? "not linked"}</strong>
            </div>
          </div>
        </section>
        <section className="card stack strong">
          <div>
            <p className="eyebrow">Version editing surface</p>
            <h2>Current stored content</h2>
          </div>
          <pre className="code-block">{JSON.stringify(version.content_json, null, 2)}</pre>
        </section>
      </div>
    </>
  );
}
