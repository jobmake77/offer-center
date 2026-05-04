# Offer Center API Contract v1

## Conventions

Base path:

```text
/api/v1
```

Response envelope:

```json
{
  "data": {},
  "meta": {},
  "error": null
}
```

Async response:

```json
{
  "data": {
    "task_id": "uuid",
    "status": "queued"
  },
  "meta": {},
  "error": null
}
```

## Authentication

All endpoints below assume an authenticated user.

## Profile

### GET `/profile`

Returns the current user profile.

### PATCH `/profile`

Request:

```json
{
  "headline": "Senior iOS Engineer and Engineering Lead",
  "years_of_experience": 12,
  "current_city": "Shanghai",
  "target_roles": ["Staff Engineer", "Engineering Manager"],
  "seniority_level": "senior",
  "summary": "Focused on product-minded engineering leadership.",
  "skills": {
    "languages": ["Swift", "Objective-C", "TypeScript"],
    "domains": ["iOS", "tooling", "platform"]
  }
}
```

## Preferences

### GET `/preferences`

Returns the current preference profile.

### PATCH `/preferences`

Request:

```json
{
  "preferred_cities": ["Shanghai", "Remote"],
  "remote_preference": "hybrid",
  "salary_expectation_min": 70000,
  "salary_expectation_max": 100000,
  "target_industries": ["Developer Tools", "AI Infrastructure"],
  "target_company_stages": ["growth", "public"],
  "deal_breakers": {
    "outsourcing": true,
    "heavy_oncall": true,
    "long_commute": true
  },
  "work_style_preferences": {
    "deep_work": 0.9,
    "people_management": 0.4,
    "cross_team_alignment": 0.7
  },
  "importance_weights": {
    "salary": 0.2,
    "growth": 0.2,
    "scope": 0.25,
    "work_content": 0.2,
    "brand": 0.05,
    "risk": 0.1
  }
}
```

## Resumes

### POST `/resumes/upload`

Multipart form upload.

Response:

```json
{
  "data": {
    "resume_id": "uuid",
    "task_id": "uuid",
    "status": "queued"
  },
  "meta": {},
  "error": null
}
```

### GET `/resumes`

Query params:

- `include_versions=true|false`

### GET `/resumes/{resumeId}`

Returns one resume and optional latest parsed payload.

### POST `/resumes/{resumeId}/parse`

Queues a re-parse.

### POST `/resumes/{resumeId}/versions`

Request:

```json
{
  "job_posting_id": "uuid",
  "version_type": "ai_tailored",
  "instructions": "Emphasize system design, team leadership, and architecture ownership."
}
```

### GET `/resume-versions/{versionId}`

Returns structured version content and linked target job if it exists.

### PATCH `/resume-versions/{versionId}`

Request:

```json
{
  "content_json": {
    "summary": "Updated summary",
    "experiences": []
  }
}
```

### POST `/resume-versions/{versionId}/export`

Request:

```json
{
  "format": "pdf"
}
```

## Jobs

### POST `/jobs/import`

Request:

```json
{
  "source_type": "paste",
  "raw_content": "JD text goes here"
}
```

Behavior:

1. create `job_raw_inputs`
2. queue `parse_job`
3. create `job_postings`
4. queue `enrich_company`
5. queue `generate_match_report`

### POST `/jobs/import-url`

Request:

```json
{
  "url": "https://example.com/jobs/123"
}
```

### GET `/jobs`

Query params:

- `q`
- `city`
- `remote_type`
- `min_salary`
- `max_risk_score`
- `source_type`
- `application_stage`
- `favorite`
- `page`
- `page_size`

### GET `/jobs/{jobId}`

Returns:

- job overview
- structured JD
- company summary
- current application summary
- latest match report summary

### POST `/jobs/{jobId}/reparse`

Queues a re-parse for the target job.

### POST `/jobs/{jobId}/archive`

Marks the job as archived for the current user.

### POST `/jobs/{jobId}/favorite`

Request:

```json
{
  "favorite": true
}
```

## Match Reports

### POST `/jobs/{jobId}/match`

Request:

```json
{
  "resume_version_id": "uuid",
  "force_refresh": false
}
```

### GET `/jobs/{jobId}/match-reports`

Returns all generated reports for the current user and job.

### GET `/match-reports/{reportId}`

Response shape:

```json
{
  "data": {
    "id": "uuid",
    "scores": {
      "hard_fit": 78,
      "skill_fit": 74,
      "work_content_fit": 88,
      "career_fit": 84,
      "risk_adjusted_value": 69,
      "overall": 79
    },
    "missing_requirements": [],
    "strengths": [],
    "weaknesses": [],
    "tailored_suggestions": [],
    "evidence": []
  },
  "meta": {},
  "error": null
}
```

### POST `/match-reports/{reportId}/generate-actions`

Creates actionable recommendation items for dashboard and job detail pages.

## Generated Assets

### POST `/assets/generate`

Request:

```json
{
  "asset_type": "cover_letter",
  "job_posting_id": "uuid",
  "resume_version_id": "uuid",
  "application_id": "uuid",
  "tone": "concise",
  "language": "en"
}
```

Allowed `asset_type` values:

- `resume`
- `cover_letter`
- `intro`
- `interview_prep`
- `salary_script`

### GET `/generated-assets/{assetId}`

Returns the generated asset content and any rendered file URL.

## Applications

### POST `/applications`

Request:

```json
{
  "job_posting_id": "uuid",
  "resume_version_id": "uuid",
  "source_channel": "company_site",
  "current_stage": "draft"
}
```

### GET `/applications`

Query params:

- `stage`
- `source_channel`
- `page`
- `page_size`

### GET `/applications/{applicationId}`

Returns:

- application summary
- current stage
- linked assets
- linked events
- linked interview summary

### PATCH `/applications/{applicationId}`

Updates notes, contact info, or next follow-up time.

### PATCH `/applications/{applicationId}/stage`

Request:

```json
{
  "current_stage": "hr_replied",
  "event_time": "2026-04-21T10:30:00+08:00",
  "note": "HR requested availability for a first-round call."
}
```

### POST `/applications/{applicationId}/events`

Request:

```json
{
  "event_type": "follow_up_sent",
  "event_time": "2026-04-21T12:00:00+08:00",
  "payload": {
    "channel": "email",
    "summary": "Shared updated resume and scheduling window."
  }
}
```

### POST `/applications/{applicationId}/reminders`

Request:

```json
{
  "next_followup_at": "2026-04-23T09:00:00+08:00"
}
```

## Interviews

### POST `/interviews`

Request:

```json
{
  "application_id": "uuid",
  "round_name": "Technical Round 1",
  "interview_type": "technical",
  "scheduled_at": "2026-04-24T15:00:00+08:00",
  "interviewer_names": ["Alice", "Bob"]
}
```

### GET `/interviews/{interviewId}`

Returns interview metadata and the latest prep asset if available.

### POST `/interviews/{interviewId}/generate-prep`

Queues an interview prep asset generation.

### PATCH `/interviews/{interviewId}`

Allows note and status updates.

## Dashboard And Insights

### GET `/dashboard/overview`

Response:

```json
{
  "data": {
    "new_jobs_24h": 12,
    "ready_to_apply": 5,
    "followups_due_today": 3,
    "interviews_upcoming": 2,
    "top_recommendations": []
  },
  "meta": {},
  "error": null
}
```

### GET `/dashboard/today-actions`

Returns normalized action items ordered by priority.

### GET `/insights/pipeline`

Returns stage distribution and recent movement.

### GET `/insights/conversion`

Returns conversion data such as:

- jobs reviewed to applications
- applications to replies
- replies to interviews
- interviews to offers

## Tasks

### GET `/tasks/{taskId}`

Response:

```json
{
  "data": {
    "id": "uuid",
    "task_type": "generate_match_report",
    "status": "running",
    "target_type": "job_posting",
    "target_id": "uuid"
  },
  "meta": {},
  "error": null
}
```

## Error Shape

```json
{
  "data": null,
  "meta": {},
  "error": {
    "code": "validation_error",
    "message": "Invalid payload",
    "details": {}
  }
}
```
