# Offer Center Page IA v1

## Product Goal

Offer Center should behave as a job search operating system:

- collect opportunities
- evaluate them quickly
- generate tailored application assets
- track every application as a pipeline
- learn from outcomes over time

## Navigation Model

Global navigation:

- Dashboard
- Jobs
- Resumes
- Applications
- Insights
- Settings

Global quick actions:

- Import JD
- Upload Resume
- Quick Capture

## Route Map

| Route | Page | Primary Goal | Core Modules | Primary CTA |
|---|---|---|---|---|
| `/dashboard` | Dashboard | Show the highest priority work for today | pipeline snapshot, top matches, follow-up queue, upcoming interviews, AI actions | Review next action |
| `/jobs/inbox` | Job Inbox | Collect and filter opportunities | source tags, dedupe state, freshness score, risk tags, search filters | Open job detail |
| `/jobs/[jobId]` | Job Detail | Make a decision on a single job | structured JD, match report, company signals, tailored assets, activity log | Create tailored version |
| `/jobs/[jobId]/analysis` | Job Analysis | Deep-dive into job quality and risks | work-content fit, career fit, hidden signals, evidence blocks | Decide apply or skip |
| `/resumes` | Resume Asset Center | Manage the master resume and reusable assets | master resume, version list, bullet library, export history | Create new version |
| `/resumes/[resumeId]/versions/[versionId]` | Resume Version Editor | Tailor one resume version for one target job | JD summary, AI suggestions, structured editor, preview panel | Export PDF |
| `/applications/board` | Application Board | Track all applications in one place | Kanban board, due reminders, conversion summary, filters | Update stage |
| `/applications/[applicationId]` | Application Detail | Track the history and next step of one application | timeline, assets, contact info, notes, reminders | Add event |
| `/interviews/[interviewId]/prep` | Interview Prep | Prepare for an interview with generated materials | self intro, highlight stories, likely questions, questions to ask, salary notes | Mark prepared |
| `/insights` | Insights | Review outcome quality and process efficiency | conversion funnel, source quality, best-performing versions, suggestion adoption | Adjust strategy |
| `/settings/profile` | Profile Settings | Maintain the candidate profile | summary, skill tags, work history, education | Save profile |
| `/settings/preferences` | Preference Settings | Maintain search preferences and constraints | cities, compensation, company stage, deal breakers, weights | Save preferences |

## Core User Flows

### Flow 1: Manual Job Evaluation

1. User opens `Job Inbox`.
2. User imports a job by paste, URL, or upload.
3. System parses the JD and computes initial signals.
4. User opens `Job Detail`.
5. User reviews the structured JD, match score, and risks.
6. User chooses `Apply`, `Skip`, or `Archive`.

### Flow 2: Tailored Resume Creation

1. User opens `Job Detail`.
2. User triggers `Create tailored version`.
3. System creates a `resume_version` linked to the target job.
4. User edits bullets in the version editor.
5. User exports PDF and optionally creates an application draft.

### Flow 3: Application Tracking

1. User creates an application from a job.
2. System opens the application in the board at `draft` or `applied`.
3. User records events such as `HR replied` or `follow-up sent`.
4. System surfaces due reminders on `Dashboard`.
5. User opens `Interview Prep` when an interview is scheduled.

## Page-Level Requirements

### Dashboard

- Must prioritize action over analytics.
- Must show top 5 jobs worth acting on.
- Must show follow-ups due today.
- Must show pending generation or parsing tasks.

### Job Inbox

- Must support deduped and raw views.
- Must support filtering by city, salary, freshness, risk, source, stage.
- Must allow bulk archive and bulk mark-interesting.

### Job Detail

- Must show a top-level recommendation:
  - apply
  - review manually
  - skip
- Must expose evidence for every important conclusion.
- Must show the current application stage if an application already exists.

### Resume Version Editor

- Must support structured editing for bullets and summaries.
- Must show JD requirements side by side with resume content.
- Must preserve a version history and export history.

### Application Board

- Must support stage transitions:
  - draft
  - ready_to_apply
  - applied
  - hr_replied
  - interview
  - offer
  - rejected
  - archived

### Interview Prep

- Must generate a stable preparation pack with reusable sections.
- Must link back to the job, company, and resume version used in the application.

## MVP Scope

Pages required for the first usable release:

- `/dashboard`
- `/jobs/inbox`
- `/jobs/[jobId]`
- `/resumes`
- `/resumes/[resumeId]/versions/[versionId]`
- `/applications/board`

Pages that can be added later:

- `/jobs/[jobId]/analysis`
- `/interviews/[interviewId]/prep`
- `/insights`
- settings sub-pages with advanced weights and privacy modes
