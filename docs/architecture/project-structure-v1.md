# Offer Center Project Structure v1

## Recommended Repository Shape

This project should start as a modular monorepo.

```text
offer-center/
├─ apps/
│  ├─ web/
│  │  ├─ app/
│  │  │  ├─ (app-shell)/
│  │  │  │  ├─ dashboard/page.tsx
│  │  │  │  ├─ jobs/
│  │  │  │  │  ├─ inbox/page.tsx
│  │  │  │  │  ├─ [jobId]/page.tsx
│  │  │  │  │  └─ [jobId]/analysis/page.tsx
│  │  │  │  ├─ resumes/
│  │  │  │  │  ├─ page.tsx
│  │  │  │  │  └─ [resumeId]/versions/[versionId]/page.tsx
│  │  │  │  ├─ applications/
│  │  │  │  │  ├─ board/page.tsx
│  │  │  │  │  └─ [applicationId]/page.tsx
│  │  │  │  ├─ interviews/[interviewId]/prep/page.tsx
│  │  │  │  ├─ insights/page.tsx
│  │  │  │  └─ settings/
│  │  │  │     ├─ profile/page.tsx
│  │  │  │     └─ preferences/page.tsx
│  │  │  ├─ api/
│  │  │  ├─ layout.tsx
│  │  │  └─ page.tsx
│  │  ├─ components/
│  │  │  ├─ dashboard/
│  │  │  ├─ jobs/
│  │  │  ├─ resumes/
│  │  │  ├─ applications/
│  │  │  └─ shared/
│  │  ├─ lib/
│  │  │  ├─ api-client/
│  │  │  ├─ formatters/
│  │  │  └─ validators/
│  │  ├─ hooks/
│  │  ├─ styles/
│  │  └─ tests/
│  └─ api/
│     ├─ app/
│     │  ├─ main.py
│     │  ├─ core/
│     │  │  ├─ config.py
│     │  │  ├─ db.py
│     │  │  ├─ security.py
│     │  │  └─ logging.py
│     │  ├─ modules/
│     │  │  ├─ identity/
│     │  │  ├─ candidate_profile/
│     │  │  ├─ resume_assets/
│     │  │  ├─ ingestion/
│     │  │  ├─ job_intelligence/
│     │  │  ├─ company_intel/
│     │  │  ├─ matching/
│     │  │  ├─ application_crm/
│     │  │  ├─ interview_prep/
│     │  │  ├─ recommendation/
│     │  │  ├─ automation/
│     │  │  └─ ai_gateway/
│     │  ├─ shared/
│     │  │  ├─ enums.py
│     │  │  ├─ exceptions.py
│     │  │  ├─ pagination.py
│     │  │  └─ tasks.py
│     │  └─ workers/
│     │     ├─ celery_app.py
│     │     └─ jobs/
│     ├─ tests/
│     └─ alembic/
├─ packages/
│  ├─ ui/
│  ├─ config/
│  └─ types/
├─ database/
│  ├─ migrations/
│  └─ seeds/
├─ docs/
│  ├─ product/
│  ├─ architecture/
│  └─ api/
└─ README.md
```

## Frontend Architecture

### App Router

Use Next.js App Router with route groups for the authenticated shell.

Recommended route groups:

- `(app-shell)` for authenticated pages
- `(marketing)` if a landing page is added later

### Frontend Module Boundaries

- `components/dashboard`: cards, lists, today-actions panels
- `components/jobs`: inbox table, detail header, analysis widgets
- `components/resumes`: version editor, bullet panels, previews
- `components/applications`: Kanban board, event timeline, reminder list
- `components/shared`: layout shell, buttons, dialog, tables, toasts

### Frontend Data Conventions

- Use `TanStack Query` for server state.
- Use `React Hook Form` for complex editing screens.
- Use `Zod` for request and form validation.
- Prefer server components for read-heavy pages and client components for local editing interactions.

## Backend Architecture

Each backend module should own its routes, schemas, services, repository functions, and background tasks.

Recommended module shape:

```text
modules/job_intelligence/
├─ models.py
├─ schemas.py
├─ repository.py
├─ service.py
├─ router.py
└─ tasks.py
```

### Core Modules

- `candidate_profile`: user profile and preferences
- `resume_assets`: resumes, resume versions, bullet libraries, export records
- `ingestion`: raw job inputs, source adapters, normalization pipeline
- `job_intelligence`: structured JD parsing, signals, risk flags, freshness
- `company_intel`: company enrichment and signal aggregation
- `matching`: score generation, evidence extraction, actionable suggestions
- `application_crm`: applications, stage transitions, reminders, events
- `interview_prep`: interview packs and preparation notes
- `recommendation`: dashboard actions and strategic recommendations
- `automation`: future RPA and semi-automatic workflows
- `ai_gateway`: LLM provider abstraction, prompts, validation, cost logging

## AI Gateway Design

The `ai_gateway` module should centralize all provider interactions.

Responsibilities:

- prompt template management
- schema-first output validation
- provider fallback
- retry policy
- token and cost accounting
- model version tracking

Never let business modules call providers directly.

## Worker Design

Recommended background jobs:

- `parse_resume`
- `parse_job`
- `embed_document`
- `dedupe_job`
- `enrich_company`
- `generate_match_report`
- `generate_asset`

All jobs should write status into a shared `tasks` table.

## API Client Boundary

The web app should call backend APIs through a typed client package:

```text
apps/web/lib/api-client/
├─ jobs.ts
├─ resumes.ts
├─ applications.ts
├─ dashboard.ts
└─ types.ts
```

This avoids fetching logic leaking into page components.

## Suggested Implementation Order

### Package 1

- database migration
- backend app bootstrap
- web app shell
- `jobs/import`
- `jobs/list`
- `resumes/upload`

### Package 2

- JD parser
- resume parser
- job detail page
- match report generation

### Package 3

- resume version editor
- tailored asset generation
- PDF export

### Package 4

- application board
- application events
- reminders
- interview prep

## Non-Goals For The First Release

- full browser automation across hostile job platforms
- heavy crawler infrastructure
- microservice split
- a separate vector database
