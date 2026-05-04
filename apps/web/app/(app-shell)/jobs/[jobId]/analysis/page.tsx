import { PageHeader } from "@/components/shared/page-header";

export default async function JobAnalysisPage({ params }: { params: Promise<{ jobId: string }> }) {
  const { jobId } = await params;

  return (
    <>
      <PageHeader
        eyebrow="Analysis"
        title={`Deep analysis for job ${jobId}`}
        description="This route is reserved for work-content fit, hidden signals, and more explicit evidence review."
      />
      <section className="card">
        <pre className="code-block">{`{
  "work_content_fit": 0.88,
  "career_fit": 0.84,
  "risk_flags": ["broad_scope", "unclear_team_size"]
}`}</pre>
      </section>
    </>
  );
}
