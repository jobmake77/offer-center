import { apiGet, safeApiGet } from "./client";

export type ApplicationListItem = {
  id: string;
  job_title: string;
  company_name: string;
  current_stage: string;
};

export function getApplications() {
  return apiGet<ApplicationListItem[]>("/applications");
}

export function getApplicationsSafe() {
  return safeApiGet<ApplicationListItem[]>("/applications", []);
}

export type ApplicationDetail = {
  id: string;
  job_posting_id: string;
  current_stage: string;
  linked_assets: Array<Record<string, unknown>>;
  linked_events: Array<{
    id: string;
    event_type: string;
    event_time: string;
    payload: Record<string, unknown>;
  }>;
  linked_interview_summary: Record<string, unknown> | null;
};

export function getApplication(applicationId: string) {
  return apiGet<ApplicationDetail>(`/applications/${applicationId}`);
}

export function getApplicationSafe(applicationId: string) {
  return safeApiGet<ApplicationDetail>(`/applications/${applicationId}`, {
    id: applicationId,
    job_posting_id: "",
    current_stage: "unknown",
    linked_assets: [],
    linked_events: [],
    linked_interview_summary: null
  });
}
