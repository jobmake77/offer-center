type FeedbackBannerProps = {
  status?: string;
  message?: string;
};

export function FeedbackBanner({ status, message }: FeedbackBannerProps) {
  if (!status || !message) {
    return null;
  }

  const tone = status === "success" ? "success" : "error";

  return (
    <section className={`feedback-banner ${tone}`} role="status" aria-live="polite">
      <strong>{tone === "success" ? "Success" : "Error"}</strong>
      <span>{message}</span>
    </section>
  );
}
