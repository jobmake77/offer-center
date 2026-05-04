"use server";

import type { Route } from "next";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { apiPatch, apiPost, apiPostFormData } from "@/lib/api-client/client";

function buildFeedbackPath(path: string, status: "success" | "error", message: string) {
  const search = new URLSearchParams({
    status,
    message
  });

  return `${path}?${search.toString()}`;
}

function redirectTo(path: string): never {
  redirect(path as Route);
}

export async function uploadResumeAction(formData: FormData) {
  const file = formData.get("resume_file");
  if (!(file instanceof File) || file.size === 0) {
    redirectTo(buildFeedbackPath("/resumes", "error", "Please choose a resume file before submitting."));
  }

  const payload = new FormData();
  payload.set("file", file);

  let destination = "/resumes";

  try {
    await apiPostFormData<{ resume_id: string }>("/resumes/upload", payload);
    revalidatePath("/resumes");
    destination = buildFeedbackPath("/resumes", "success", "Resume uploaded successfully.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to upload resume.";
    destination = buildFeedbackPath("/resumes", "error", message);
  }

  redirectTo(destination);
}

export async function importJobAction(formData: FormData) {
  const rawContent = String(formData.get("raw_content") || "").trim();

  if (!rawContent) {
    redirectTo(buildFeedbackPath("/jobs/inbox", "error", "Paste the JD content before importing."));
  }

  let destination = "/jobs/inbox";

  try {
    const response = await apiPost<{ job_id: string }>("/jobs/import", {
      source_type: "paste",
      raw_content: rawContent
    });

    revalidatePath("/jobs/inbox");
    revalidatePath("/dashboard");
    destination = buildFeedbackPath(`/jobs/${response.job_id}`, "success", "Job imported successfully.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to import the job.";
    destination = buildFeedbackPath("/jobs/inbox", "error", message);
  }

  redirectTo(destination);
}

export async function importJobUrlAction(formData: FormData) {
  const url = String(formData.get("url") || "").trim();

  if (!url) {
    redirectTo(buildFeedbackPath("/jobs/inbox", "error", "Paste the job URL before importing."));
  }

  let destination = "/jobs/inbox";

  try {
    const response = await apiPost<{ job_id: string }>("/jobs/import-url", {
      url
    });

    revalidatePath("/jobs/inbox");
    revalidatePath("/dashboard");
    destination = buildFeedbackPath(`/jobs/${response.job_id}`, "success", "Job URL imported successfully.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to import the job URL.";
    destination = buildFeedbackPath("/jobs/inbox", "error", message);
  }

  redirectTo(destination);
}

export async function createResumeVersionAction(formData: FormData) {
  const resumeId = String(formData.get("resume_id") || "");
  const jobId = String(formData.get("job_id") || "");
  const instructions = String(formData.get("instructions") || "");

  if (!resumeId || !jobId) {
    redirectTo(buildFeedbackPath(`/jobs/${jobId || ""}`, "error", "Resume and job are required."));
  }

  let destination = `/jobs/${jobId}`;

  try {
    const response = await apiPost<{ version_id: string }>(`/resumes/${resumeId}/versions`, {
      job_posting_id: jobId,
      version_type: "ai_tailored",
      instructions
    });

    revalidatePath(`/jobs/${jobId}`);
    revalidatePath("/resumes");
    destination = buildFeedbackPath(
      `/resumes/${resumeId}/versions/${response.version_id}`,
      "success",
      "Resume version created successfully."
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to create resume version.";
    destination = buildFeedbackPath(`/jobs/${jobId}`, "error", message);
  }

  redirectTo(destination);
}

export async function generateMatchReportAction(formData: FormData) {
  const jobId = String(formData.get("job_id") || "");
  const resumeVersionId = String(formData.get("resume_version_id") || "");

  if (!jobId || !resumeVersionId) {
    redirectTo(buildFeedbackPath(`/jobs/${jobId || ""}`, "error", "Select a resume version first."));
  }

  let destination = `/jobs/${jobId}`;

  try {
    await apiPost(`/jobs/${jobId}/match`, {
      resume_version_id: resumeVersionId,
      force_refresh: true
    });

    revalidatePath(`/jobs/${jobId}`);
    destination = buildFeedbackPath(`/jobs/${jobId}`, "success", "Match report generated successfully.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to generate match report.";
    destination = buildFeedbackPath(`/jobs/${jobId}`, "error", message);
  }

  redirectTo(destination);
}

export async function createApplicationAction(formData: FormData) {
  const jobId = String(formData.get("job_id") || "");
  const resumeVersionId = String(formData.get("resume_version_id") || "");
  const sourceChannel = String(formData.get("source_channel") || "manual");

  if (!jobId || !resumeVersionId) {
    redirectTo(buildFeedbackPath(`/jobs/${jobId || ""}`, "error", "Select a resume version before creating an application."));
  }

  let destination = `/jobs/${jobId}`;

  try {
    const response = await apiPost<{ application_id: string; status?: string }>(`/applications`, {
      job_posting_id: jobId,
      resume_version_id: resumeVersionId,
      source_channel: sourceChannel,
      current_stage: "ready_to_apply"
    });

    revalidatePath(`/jobs/${jobId}`);
    revalidatePath("/applications/board");
    revalidatePath("/dashboard");
    destination = buildFeedbackPath(
      `/applications/${response.application_id}`,
      "success",
      response.status === "existing"
        ? "Application already exists. Opening the tracked record."
        : "Application created and marked ready to apply."
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to create application.";
    destination = buildFeedbackPath(`/jobs/${jobId}`, "error", message);
  }

  redirectTo(destination);
}

export async function updateApplicationStageAction(formData: FormData) {
  const applicationId = String(formData.get("application_id") || "");
  const currentStage = String(formData.get("current_stage") || "");
  const note = String(formData.get("note") || "");

  if (!applicationId || !currentStage) {
    redirectTo(buildFeedbackPath(`/applications/${applicationId || ""}`, "error", "Application and target stage are required."));
  }

  let destination = `/applications/${applicationId}`;

  try {
    await apiPatch(`/applications/${applicationId}/stage`, {
      current_stage: currentStage,
      event_time: new Date().toISOString(),
      note
    });

    revalidatePath(`/applications/${applicationId}`);
    revalidatePath("/applications/board");
    revalidatePath("/dashboard");
    destination = buildFeedbackPath(`/applications/${applicationId}`, "success", "Application stage updated successfully.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to update application stage.";
    destination = buildFeedbackPath(`/applications/${applicationId}`, "error", message);
  }

  redirectTo(destination);
}

export async function createApplicationEventAction(formData: FormData) {
  const applicationId = String(formData.get("application_id") || "");
  const eventType = String(formData.get("event_type") || "");
  const summary = String(formData.get("summary") || "");

  if (!applicationId || !eventType) {
    redirectTo(buildFeedbackPath(`/applications/${applicationId || ""}`, "error", "Application and event type are required."));
  }

  let destination = `/applications/${applicationId}`;

  try {
    await apiPost(`/applications/${applicationId}/events`, {
      event_type: eventType,
      event_time: new Date().toISOString(),
      payload: {
        summary
      }
    });

    revalidatePath(`/applications/${applicationId}`);
    destination = buildFeedbackPath(`/applications/${applicationId}`, "success", "Application event added successfully.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to add application event.";
    destination = buildFeedbackPath(`/applications/${applicationId}`, "error", message);
  }

  redirectTo(destination);
}
