import { PageHeader } from "@/components/shared/page-header";

export default async function InterviewPrepPage({ params }: { params: Promise<{ interviewId: string }> }) {
  const { interviewId } = await params;

  return (
    <>
      <PageHeader
        eyebrow="Interview Prep"
        title={`Interview prep ${interviewId}`}
        description="This route should generate a stable preparation pack tied to the job, the resume version, and the interviewer context."
      />
      <section className="card">
        <h2>Prep sections</h2>
        <ul className="list">
          <li className="list-item">Self introduction</li>
          <li className="list-item">Highlight stories</li>
          <li className="list-item">Likely questions and risks</li>
          <li className="list-item">Questions to ask</li>
        </ul>
      </section>
    </>
  );
}
