# offer-center

Offer Center is a job search workspace focused on decision quality instead of bulk applications.

## Direction Guardrails

- Optimize for deliberate decisions, not application volume.
- Treat each job as an evidence-backed decision record.
- Keep resume variants, match reports, applications, reminders, and interview prep linked to the same opportunity.
- Prefer one working vertical slice over disconnected feature breadth.
- Avoid automated mass-apply behavior unless the product explicitly introduces a reviewed approval flow.

## Documents

- [Product Page IA v1](docs/product/page-ia-v1.md)
- [Project Structure v1](docs/architecture/project-structure-v1.md)
- [API Contract v1](docs/api/api-contract-v1.md)
- [Initial PostgreSQL Migration](database/migrations/001_init_offer_center.sql)

## Recommended Build Order

1. Create the database from `database/migrations/001_init_offer_center.sql`.
2. Scaffold the monorepo structure from `docs/architecture/project-structure-v1.md`.
3. Build the backend APIs following `docs/api/api-contract-v1.md`.
4. Implement the page routes from `docs/product/page-ia-v1.md` against the typed API client.
5. Tighten the main vertical slice: import job, upload resume, create tailored version, generate match report, create application, and surface the next action.

## Product Focus

- Import jobs from paste, URL, upload, email, or crawler adapters.
- Parse job descriptions into structured intelligence.
- Match jobs against a master resume and tailored resume versions.
- Generate actionable assets such as tailored resumes, cover letters, and interview prep.
- Track the application pipeline with reminders, events, and outcome feedback.
