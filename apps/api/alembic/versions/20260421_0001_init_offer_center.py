from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "20260421_0001"
down_revision = None
branch_labels = None
depends_on = None


def _read_sql_statements() -> list[str]:
    sql_path = Path(__file__).resolve().parents[4] / "database" / "migrations" / "001_init_offer_center.sql"
    content = sql_path.read_text(encoding="utf-8")

    statements: list[str] = []
    buffer: list[str] = []

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        buffer.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(buffer))
            buffer = []

    if buffer:
        statements.append("\n".join(buffer))

    return statements


def upgrade() -> None:
    for statement in _read_sql_statements():
        op.execute(statement)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS tasks CASCADE;")
    op.execute("DROP TABLE IF EXISTS feedback_events CASCADE;")
    op.execute("DROP TABLE IF EXISTS interviews CASCADE;")
    op.execute("DROP TABLE IF EXISTS generated_assets CASCADE;")
    op.execute("DROP TABLE IF EXISTS application_events CASCADE;")
    op.execute("DROP TABLE IF EXISTS applications CASCADE;")
    op.execute("DROP TABLE IF EXISTS recommendations CASCADE;")
    op.execute("DROP TABLE IF EXISTS match_reports CASCADE;")
    op.execute("DROP TABLE IF EXISTS resume_bullets CASCADE;")
    op.execute("DROP TABLE IF EXISTS resume_versions CASCADE;")
    op.execute("DROP TABLE IF EXISTS job_signals CASCADE;")
    op.execute("DROP TABLE IF EXISTS company_signals CASCADE;")
    op.execute("DROP TABLE IF EXISTS job_postings CASCADE;")
    op.execute("DROP TABLE IF EXISTS companies CASCADE;")
    op.execute("DROP TABLE IF EXISTS job_raw_inputs CASCADE;")
    op.execute("DROP TABLE IF EXISTS resumes CASCADE;")
    op.execute("DROP TABLE IF EXISTS preference_profiles CASCADE;")
    op.execute("DROP TABLE IF EXISTS user_profiles CASCADE;")
    op.execute("DROP TABLE IF EXISTS users CASCADE;")

    op.execute("DROP TYPE IF EXISTS interview_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS recommendation_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS asset_format CASCADE;")
    op.execute("DROP TYPE IF EXISTS asset_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS application_stage CASCADE;")
    op.execute("DROP TYPE IF EXISTS job_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS source_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS resume_version_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS task_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS parser_status CASCADE;")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto;")
