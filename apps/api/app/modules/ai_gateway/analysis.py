from __future__ import annotations

from typing import Any

from app.modules.ai_gateway.client import AIProviderError, request_json_from_kimi
from app.modules.job_intelligence.models import JobPosting
from app.modules.resume_assets.models import Resume, ResumeVersion


def parse_job_with_ai(raw_content: str) -> dict[str, Any]:
    system_prompt = """
You are a senior recruiting intelligence analyst.
Extract a normalized job description and return valid JSON only.
Do not include markdown fences.
""".strip()

    user_prompt = f"""
Analyze the following job description and return a JSON object with this exact shape:
{{
  "title": "string",
  "normalized_title": "string",
  "city": "string or null",
  "country": "string or null",
  "remote_type": "onsite|hybrid|remote|null",
  "salary_min": "integer or null",
  "salary_max": "integer or null",
  "salary_currency": "string or null",
  "experience_min_years": "integer or null",
  "experience_max_years": "integer or null",
  "education_requirement": "string or null",
  "employment_type": "string or null",
  "summary": "short summary",
  "skill_tags": ["string"],
  "responsibility_tags": ["string"],
  "hidden_signals": {{
    "team_stage": "string or null",
    "delivery_pressure": "low|medium|high|null",
    "scope": "string or null"
  }},
  "risk_flags": ["string"],
  "quality_score": "number from 0 to 100"
}}

Job description:
{raw_content}
""".strip()

    return request_json_from_kimi(system_prompt=system_prompt, user_prompt=user_prompt)


def parse_resume_with_ai(resume_text: str) -> dict[str, Any]:
    system_prompt = """
You are a career document analyst.
Extract structured resume data and return valid JSON only.
Do not include markdown fences.
""".strip()

    user_prompt = f"""
Analyze the following resume text and return a JSON object with this exact shape:
{{
  "headline": "string",
  "summary": "string",
  "core_skills": ["string"],
  "domains": ["string"],
  "experience_level": "junior|mid|senior|staff|principal|unknown",
  "experience_items": [
    {{
      "company": "string or null",
      "role": "string or null",
      "achievement": "string"
    }}
  ],
  "strength_signals": ["string"]
}}

Resume text:
{resume_text}
""".strip()

    return request_json_from_kimi(system_prompt=system_prompt, user_prompt=user_prompt)


def build_match_report_with_ai(job: JobPosting, resume: Resume | None, resume_version: ResumeVersion) -> dict[str, Any]:
    system_prompt = """
You are an expert recruiting strategist.
Compare a candidate resume against a target job and return valid JSON only.
Do not include markdown fences.
""".strip()

    user_prompt = f"""
Return a JSON object with this exact shape:
{{
  "scores": {{
    "hard_fit": "number from 0 to 100",
    "skill_fit": "number from 0 to 100",
    "work_content_fit": "number from 0 to 100",
    "career_fit": "number from 0 to 100",
    "risk_adjusted_value": "number from 0 to 100",
    "overall": "number from 0 to 100"
  }},
  "missing_requirements": ["string"],
  "strengths": ["string"],
  "weaknesses": ["string"],
  "tailored_suggestions": ["string"],
  "evidence": [
    {{
      "type": "string",
      "value": "string or number"
    }}
  ]
}}

Job title:
{job.title}

Structured job data:
{job.structured_jd}

Job description text:
{job.description_text}

Resume parsed data:
{resume.parsed_json if resume else {}}

Resume raw text:
{resume.parsed_text if resume else ""}

Resume version content:
{resume_version.content_json}
""".strip()

    return request_json_from_kimi(system_prompt=system_prompt, user_prompt=user_prompt)


__all__ = [
    "AIProviderError",
    "build_match_report_with_ai",
    "parse_job_with_ai",
    "parse_resume_with_ai",
]
