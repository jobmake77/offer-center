import { apiGet, safeApiGet } from "./client";

export type ResumeListItem = {
  id: string;
  name: string;
  is_master: boolean;
  parser_status: string;
};

export function getResumes() {
  return apiGet<ResumeListItem[]>("/resumes");
}

export function getResumesSafe() {
  return safeApiGet<ResumeListItem[]>("/resumes", []);
}

export type ResumeVersionDetail = {
  id: string;
  resume_id: string;
  job_posting_id: string | null;
  version_name: string;
  version_type: string;
  content_json: Record<string, unknown>;
  generation_status: string;
};

export type ResumeVersionListItem = {
  id: string;
  resume_id: string;
  job_posting_id: string | null;
  version_name: string;
  version_type: string;
  generation_status: string;
};

export function getResumeVersion(versionId: string) {
  return apiGet<ResumeVersionDetail>(`/resume-versions/${versionId}`);
}

export function getResumeVersionSafe(versionId: string) {
  return safeApiGet<ResumeVersionDetail>(`/resume-versions/${versionId}`, {
    id: versionId,
    resume_id: "",
    job_posting_id: null,
    version_name: "Unavailable Version",
    version_type: "unknown",
    content_json: {},
    generation_status: "unavailable"
  });
}

export function getResumeVersions(params?: {
  resumeId?: string;
  jobPostingId?: string;
}) {
  const search = new URLSearchParams();
  if (params?.resumeId) {
    search.set("resume_id", params.resumeId);
  }
  if (params?.jobPostingId) {
    search.set("job_posting_id", params.jobPostingId);
  }

  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiGet<ResumeVersionListItem[]>(`/resume-versions${suffix}`);
}

export function getResumeVersionsSafe(params?: {
  resumeId?: string;
  jobPostingId?: string;
}) {
  const search = new URLSearchParams();
  if (params?.resumeId) {
    search.set("resume_id", params.resumeId);
  }
  if (params?.jobPostingId) {
    search.set("job_posting_id", params.jobPostingId);
  }

  const suffix = search.toString() ? `?${search.toString()}` : "";
  return safeApiGet<ResumeVersionListItem[]>(`/resume-versions${suffix}`, []);
}
