import { PageHeader } from "@/components/shared/page-header";

export default function InsightsPage() {
  return (
    <>
      <PageHeader
        eyebrow="Insights"
        title="Learn from outcomes and tighten the loop."
        description="Insights should show conversion, source quality, and which tailored strategies actually produce replies and interviews."
      />
      <div className="grid two">
        <section className="card">
          <h2>Conversion funnel</h2>
          <p className="muted">Reviewed → applied → replied → interviewed → offered.</p>
        </section>
        <section className="card">
          <h2>Source quality</h2>
          <p className="muted">Company sites and trusted referrals should outperform noisy aggregators over time.</p>
        </section>
      </div>
    </>
  );
}

