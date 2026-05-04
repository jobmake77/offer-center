import { apiGet, safeApiGet } from "./client";

export type JobListItem = {
  id: string;
  title: string;
  company_name: string;
  city: string;
  score: number;
  risk_level: string;
};

export function getJobs() {
  return apiGet<JobListItem[]>("/jobs");
}

export function getJobsSafe() {
  return safeApiGet<JobListItem[]>("/jobs", []);
}

export type JobDetail = {
  id: string;
  title: string;
  structured_jd: Record<string, unknown>;
  company_summary: Record<string, unknown>;
  current_application_summary: Record<string, unknown> | null;
  latest_match_report_summary: Record<string, unknown> | null;
};

export function getJob(jobId: string) {
  return apiGet<JobDetail>(`/jobs/${jobId}`);
}

export function getJobSafe(jobId: string) {
  return safeApiGet<JobDetail>(`/jobs/${jobId}`, {
    id: jobId,
    title: "Unavailable Job",
    structured_jd: {},
    company_summary: {},
    current_application_summary: null,
    latest_match_report_summary: null
  });
}

export type MatchReport = {
  id: string;
  scores: {
    hard_fit: number;
    skill_fit: number;
    work_content_fit: number;
    career_fit: number;
    risk_adjusted_value: number;
    overall: number;
  };
  missing_requirements: string[];
  strengths: string[];
  weaknesses: string[];
  tailored_suggestions: string[];
  evidence: Array<Record<string, unknown>>;
};

export function getMatchReports(jobId: string) {
  return apiGet<MatchReport[]>(`/jobs/${jobId}/match-reports`);
}

export function getMatchReportsSafe(jobId: string) {
  return safeApiGet<MatchReport[]>(`/jobs/${jobId}/match-reports`, []);
}
