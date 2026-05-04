import { apiGet, safeApiGet } from "./client";

export type DashboardOverview = {
  new_jobs_24h: number;
  ready_to_apply: number;
  followups_due_today: number;
  interviews_upcoming: number;
  top_recommendations: Array<{ id: string; title: string }>;
};

export function getDashboardOverview() {
  return apiGet<DashboardOverview>("/dashboard/overview");
}

export function getDashboardOverviewSafe() {
  return safeApiGet<DashboardOverview>("/dashboard/overview", {
    new_jobs_24h: 0,
    ready_to_apply: 0,
    followups_due_today: 0,
    interviews_upcoming: 0,
    top_recommendations: []
  });
}
