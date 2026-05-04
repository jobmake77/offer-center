CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE parser_status AS ENUM ('pending', 'running', 'succeeded', 'failed');
CREATE TYPE task_status AS ENUM ('queued', 'running', 'succeeded', 'failed', 'cancelled');
CREATE TYPE resume_version_type AS ENUM ('master', 'manual', 'ai_tailored');
CREATE TYPE source_type AS ENUM ('paste', 'url', 'upload', 'email', 'crawler');
CREATE TYPE job_status AS ENUM ('active', 'archived', 'hidden');
CREATE TYPE application_stage AS ENUM (
  'draft',
  'ready_to_apply',
  'applied',
  'hr_replied',
  'interview',
  'offer',
  'rejected',
  'archived'
);
CREATE TYPE asset_type AS ENUM ('resume', 'cover_letter', 'intro', 'interview_prep', 'salary_script');
CREATE TYPE asset_format AS ENUM ('markdown', 'json', 'pdf');
CREATE TYPE recommendation_type AS ENUM ('apply', 'skip', 'rewrite', 'followup', 'learn');
CREATE TYPE interview_type AS ENUM ('hr', 'technical', 'hiring_manager', 'system_design', 'other');

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  name TEXT,
  locale TEXT NOT NULL DEFAULT 'zh-CN',
  timezone TEXT NOT NULL DEFAULT 'Asia/Shanghai',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  headline TEXT,
  years_of_experience INT,
  current_city TEXT,
  target_roles TEXT[] NOT NULL DEFAULT '{}',
  seniority_level TEXT,
  summary TEXT,
  skills JSONB NOT NULL DEFAULT '{}'::jsonb,
  work_history_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  education_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id)
);

CREATE TABLE preference_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  preferred_cities TEXT[] NOT NULL DEFAULT '{}',
  remote_preference TEXT,
  salary_expectation_min INT,
  salary_expectation_max INT,
  target_industries TEXT[] NOT NULL DEFAULT '{}',
  target_company_stages TEXT[] NOT NULL DEFAULT '{}',
  deal_breakers JSONB NOT NULL DEFAULT '{}'::jsonb,
  work_style_preferences JSONB NOT NULL DEFAULT '{}'::jsonb,
  importance_weights JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id)
);

CREATE TABLE resumes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  source_file_url TEXT,
  source_file_type TEXT,
  parser_status parser_status NOT NULL DEFAULT 'pending',
  parsed_text TEXT,
  parsed_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  is_master BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE job_raw_inputs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  source_type source_type NOT NULL,
  source_ref TEXT,
  raw_content TEXT,
  raw_html TEXT,
  raw_file_url TEXT,
  ingestion_status parser_status NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  normalized_name TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  website TEXT,
  industry TEXT,
  company_stage TEXT,
  size_range TEXT,
  headquarters TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE job_postings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
  raw_input_id UUID REFERENCES job_raw_inputs(id) ON DELETE SET NULL,
  dedupe_group_id UUID,
  title TEXT NOT NULL,
  normalized_title TEXT,
  city TEXT,
  country TEXT,
  remote_type TEXT,
  salary_min INT,
  salary_max INT,
  salary_currency TEXT,
  experience_min_years INT,
  experience_max_years INT,
  education_requirement TEXT,
  employment_type TEXT,
  description_text TEXT,
  structured_jd JSONB NOT NULL DEFAULT '{}'::jsonb,
  skill_tags TEXT[] NOT NULL DEFAULT '{}',
  responsibility_tags TEXT[] NOT NULL DEFAULT '{}',
  hidden_signals JSONB NOT NULL DEFAULT '{}'::jsonb,
  risk_flags TEXT[] NOT NULL DEFAULT '{}',
  freshness_score NUMERIC(5,2),
  quality_score NUMERIC(5,2),
  is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
  status job_status NOT NULL DEFAULT 'active',
  published_at TIMESTAMPTZ,
  last_seen_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE company_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  signal_type TEXT NOT NULL,
  source TEXT,
  signal_value JSONB NOT NULL DEFAULT '{}'::jsonb,
  confidence NUMERIC(4,3),
  observed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE job_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  signal_type TEXT NOT NULL,
  value JSONB NOT NULL DEFAULT '{}'::jsonb,
  confidence NUMERIC(4,3),
  evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE resume_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_posting_id UUID REFERENCES job_postings(id) ON DELETE SET NULL,
  version_name TEXT NOT NULL,
  version_type resume_version_type NOT NULL,
  content_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  rendered_markdown TEXT,
  export_pdf_url TEXT,
  generation_status task_status NOT NULL DEFAULT 'queued',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE resume_bullets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  resume_version_id UUID REFERENCES resume_versions(id) ON DELETE CASCADE,
  section_type TEXT NOT NULL,
  company_name TEXT,
  role_name TEXT,
  bullet_text TEXT NOT NULL,
  metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
  tags TEXT[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE match_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  resume_version_id UUID REFERENCES resume_versions(id) ON DELETE SET NULL,
  hard_fit_score NUMERIC(5,2),
  skill_fit_score NUMERIC(5,2),
  work_content_fit_score NUMERIC(5,2),
  career_fit_score NUMERIC(5,2),
  risk_adjusted_value_score NUMERIC(5,2),
  overall_score NUMERIC(5,2),
  missing_requirements JSONB NOT NULL DEFAULT '[]'::jsonb,
  strengths JSONB NOT NULL DEFAULT '[]'::jsonb,
  weaknesses JSONB NOT NULL DEFAULT '[]'::jsonb,
  tailored_suggestions JSONB NOT NULL DEFAULT '[]'::jsonb,
  evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
  model_version TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_posting_id UUID REFERENCES job_postings(id) ON DELETE CASCADE,
  recommendation_type recommendation_type NOT NULL,
  priority INT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  action_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  status TEXT NOT NULL DEFAULT 'open',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  resume_version_id UUID REFERENCES resume_versions(id) ON DELETE SET NULL,
  cover_letter_asset_id UUID,
  current_stage application_stage NOT NULL DEFAULT 'draft',
  source_channel TEXT,
  applied_at TIMESTAMPTZ,
  next_followup_at TIMESTAMPTZ,
  contact_name TEXT,
  contact_email TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE application_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  event_time TIMESTAMPTZ NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE generated_assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  application_id UUID REFERENCES applications(id) ON DELETE CASCADE,
  job_posting_id UUID REFERENCES job_postings(id) ON DELETE CASCADE,
  asset_type asset_type NOT NULL,
  format asset_format NOT NULL,
  content JSONB NOT NULL DEFAULT '{}'::jsonb,
  rendered_text TEXT,
  file_url TEXT,
  generation_status task_status NOT NULL DEFAULT 'queued',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE applications
  ADD CONSTRAINT applications_cover_letter_asset_id_fkey
  FOREIGN KEY (cover_letter_asset_id)
  REFERENCES generated_assets(id)
  ON DELETE SET NULL;

CREATE TABLE interviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  round_name TEXT,
  interview_type interview_type NOT NULL DEFAULT 'other',
  scheduled_at TIMESTAMPTZ,
  interviewer_names TEXT[] NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'scheduled',
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE feedback_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_posting_id UUID REFERENCES job_postings(id) ON DELETE CASCADE,
  application_id UUID REFERENCES applications(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  task_type TEXT NOT NULL,
  target_type TEXT,
  target_id UUID,
  status task_status NOT NULL DEFAULT 'queued',
  input JSONB NOT NULL DEFAULT '{}'::jsonb,
  output JSONB NOT NULL DEFAULT '{}'::jsonb,
  error_message TEXT,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_is_master ON resumes(user_id, is_master);
CREATE INDEX idx_job_raw_inputs_user_id ON job_raw_inputs(user_id, source_type);
CREATE INDEX idx_job_postings_user_status ON job_postings(user_id, status);
CREATE INDEX idx_job_postings_published_at ON job_postings(published_at DESC);
CREATE INDEX idx_job_postings_skill_tags ON job_postings USING GIN(skill_tags);
CREATE INDEX idx_job_postings_responsibility_tags ON job_postings USING GIN(responsibility_tags);
CREATE INDEX idx_job_postings_risk_flags ON job_postings USING GIN(risk_flags);
CREATE INDEX idx_resume_versions_resume_id ON resume_versions(resume_id);
CREATE INDEX idx_match_reports_job_posting_id ON match_reports(job_posting_id);
CREATE INDEX idx_applications_user_stage ON applications(user_id, current_stage);
CREATE INDEX idx_application_events_application_id ON application_events(application_id, event_time DESC);
CREATE INDEX idx_generated_assets_application_id ON generated_assets(application_id);
CREATE INDEX idx_feedback_events_user_type ON feedback_events(user_id, event_type);
CREATE INDEX idx_tasks_status ON tasks(status, created_at DESC);
