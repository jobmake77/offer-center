import {
  createApplicationEventAction,
  updateApplicationStageAction
} from "@/app/actions";
import Link from "next/link";

import { getApplicationSafe } from "@/lib/api-client/applications";
import { FeedbackBanner } from "@/components/shared/feedback-banner";
import { PageHeader } from "@/components/shared/page-header";
import { SubmitButton } from "@/components/shared/submit-button";
import { SummaryCard } from "@/components/shared/summary-card";

export default async function ApplicationDetailPage({
  params,
  searchParams
}: {
  params: Promise<{ applicationId: string }>;
  searchParams?: Promise<{ status?: string; message?: string }>;
}) {
  const { applicationId } = await params;
  const feedback = (await searchParams) ?? {};
  const application = await getApplicationSafe(applicationId);
  const currentStageLabel = application.current_stage
    .split("_")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");

  return (
    <>
      <PageHeader
        eyebrow="Application Detail"
        title={application.job_title}
        description="This route should combine timeline events, generated assets, contact context, and the next follow-up."
        meta={[
          { label: "Current stage", value: currentStageLabel },
          { label: "Events", value: String(application.linked_events.length) },
          { label: "Company", value: application.company_name }
        ]}
        actions={
          <div className="button-row">
            <Link className="button" href="/applications/board">
              Back to board
            </Link>
            <Link className="button ghost" href={`/jobs/${application.job_posting_id}`}>
              Open job
            </Link>
          </div>
        }
      />
      <FeedbackBanner status={feedback.status} message={feedback.message} />
      <div className="grid three">
        <SummaryCard title="Current stage" value={currentStageLabel} hint="The latest committed point in the application timeline." tone="accent" />
        <SummaryCard title="Timeline entries" value={String(application.linked_events.length)} hint="Every stage change and follow-up should be logged here." />
        <SummaryCard title="Linked assets" value={String(application.linked_assets.length)} hint="Generated assets or supporting materials connected to this application." />
      </div>
      <div className="grid two">
        <section className="card stack">
          <div>
            <p className="eyebrow">Workflow control</p>
            <h2>Update stage</h2>
            <p className="helper-copy">Use this when the external state actually changed. The workspace will persist the transition and append a timeline event.</p>
          </div>
          <form action={updateApplicationStageAction} className="form-grid">
            <input type="hidden" name="application_id" value={application.id} />
            <div className="form-row">
              <label className="field-label" htmlFor="current_stage">
                Stage
              </label>
              <select className="select-input" id="current_stage" name="current_stage" defaultValue={application.current_stage}>
                <option value="draft">draft</option>
                <option value="ready_to_apply">ready_to_apply</option>
                <option value="applied">applied</option>
                <option value="hr_replied">hr_replied</option>
                <option value="interview">interview</option>
                <option value="offer">offer</option>
                <option value="rejected">rejected</option>
                <option value="archived">archived</option>
              </select>
            </div>
            <div className="form-row">
              <label className="field-label" htmlFor="note">
                Note
              </label>
              <textarea className="text-area" id="note" name="note" placeholder="Optional context for the stage change." />
            </div>
            <div className="button-row">
              <SubmitButton
                label="Update Stage"
                pendingLabel="Updating Stage..."
                pendingHint="Recording the transition and appending a timeline event."
              />
            </div>
          </form>
          <div className="detail-rows">
            <div className="detail-row">
              <span>Best for</span>
              <strong>Real transitions like applied, replied, interview, offer, or reject.</strong>
            </div>
          </div>
        </section>
        <section className="card stack">
          <div>
            <p className="eyebrow">Timeline detail</p>
            <h2>Add event</h2>
            <p className="helper-copy">Use this for context that matters but should not change the formal stage: follow-ups, notes, calls, or resume refreshes.</p>
          </div>
          <form action={createApplicationEventAction} className="form-grid">
            <input type="hidden" name="application_id" value={application.id} />
            <div className="form-row">
              <label className="field-label" htmlFor="event_type">
                Event type
              </label>
              <select className="select-input" id="event_type" name="event_type" defaultValue="follow_up_sent">
                <option value="follow_up_sent">follow_up_sent</option>
                <option value="resume_updated">resume_updated</option>
                <option value="note_added">note_added</option>
                <option value="call_scheduled">call_scheduled</option>
              </select>
            </div>
            <div className="form-row">
              <label className="field-label" htmlFor="summary">
                Summary
              </label>
              <textarea className="text-area" id="summary" name="summary" placeholder="Shared updated resume and availability window." />
            </div>
            <div className="button-row">
              <SubmitButton
                label="Add Event"
                pendingLabel="Adding Event..."
                pendingHint="Writing the event into the application timeline."
                variant="secondary"
              />
            </div>
          </form>
          <div className="detail-rows">
            <div className="detail-row">
              <span>Best for</span>
              <strong>Operational notes that future-you will need when the process gets noisy.</strong>
            </div>
          </div>
        </section>
      </div>
      <section className="card stack">
        <div className="split">
          <div>
            <p className="eyebrow">Timeline</p>
            <h2>Keep the narrative legible.</h2>
          </div>
          <span className="pill neutral">{application.linked_events.length} events</span>
        </div>
        {application.linked_events.length === 0 ? (
          <div className="empty-state">
            <p className="helper-copy">No events have been recorded for this application yet.</p>
          </div>
        ) : (
          <ul className="timeline-list">
            {application.linked_events.map((event) => (
              <li className="timeline-item" key={event.id}>
                <div className="timeline-item-header">
                  <strong>{event.event_type.replaceAll("_", " ")}</strong>
                  <span className="muted">{event.event_time}</span>
                </div>
                {"summary" in event.payload && typeof event.payload.summary === "string" ? (
                  <p className="helper-copy">{event.payload.summary}</p>
                ) : null}
                {"note" in event.payload && typeof event.payload.note === "string" && event.payload.note ? (
                  <p className="helper-copy">{event.payload.note}</p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
