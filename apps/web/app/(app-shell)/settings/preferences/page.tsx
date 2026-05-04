import { PageHeader } from "@/components/shared/page-header";

export default function PreferenceSettingsPage() {
  return (
    <>
      <PageHeader
        eyebrow="Preferences"
        title="Search strategy and deal-breaker settings"
        description="Preferences should encode target geographies, compensation, work style, company stage, and clear no-go constraints."
      />
      <section className="card">
        <p className="muted">This page will later expose scoring weights and privacy mode settings.</p>
      </section>
    </>
  );
}

