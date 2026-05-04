import { PageHeader } from "@/components/shared/page-header";

export default function ProfileSettingsPage() {
  return (
    <>
      <PageHeader
        eyebrow="Profile"
        title="Candidate profile settings"
        description="The profile should remain stable and reusable across every targeted application asset."
      />
      <section className="card">
        <p className="muted">This page will hold the parsed summary, experience baseline, and reusable skill metadata.</p>
      </section>
    </>
  );
}

