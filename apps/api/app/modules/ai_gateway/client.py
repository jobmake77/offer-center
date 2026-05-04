from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings


class AIProviderError(RuntimeError):
    pass


def _extract_json_block(content: str) -> dict[str, Any]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    return json.loads(cleaned)


def is_kimi_enabled() -> bool:
    settings = get_settings()
    return settings.llm_provider.lower() == "kimi" and bool(settings.moonshot_api_key)


def is_gemini_enabled() -> bool:
    settings = get_settings()
    return settings.llm_provider.lower() == "gemini" and bool(settings.gemini_api_key)


def get_ai_model_label() -> str:
    settings = get_settings()
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        return f"gemini:{settings.gemini_model}"
    if provider == "kimi":
        return f"moonshot:{settings.moonshot_model}"
    return "scaffold-v1"


def request_json_from_kimi(
    *,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
) -> dict[str, Any]:
    settings = get_settings()
    if not is_kimi_enabled():
        raise AIProviderError("Kimi is not configured")

    payload = {
        "model": settings.moonshot_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }

    request = Request(
        url=f"{settings.moonshot_base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.moonshot_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.moonshot_timeout_seconds) as response:
            raw_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="ignore")
        raise AIProviderError(f"Kimi request failed with status {error.code}: {error_body}") from error
    except URLError as error:
        raise AIProviderError(f"Kimi request failed: {error.reason}") from error

    choices = raw_payload.get("choices") or []
    if not choices:
        raise AIProviderError("Kimi returned no choices")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") for part in content if isinstance(part, dict) and part.get("type") == "text"
        )

    if not isinstance(content, str) or not content.strip():
        raise AIProviderError("Kimi returned empty content")

    try:
        return _extract_json_block(content)
    except json.JSONDecodeError as error:
        raise AIProviderError(f"Kimi returned invalid JSON: {content}") from error


def request_json_from_gemini(
    *,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
) -> dict[str, Any]:
    settings = get_settings()
    if not is_gemini_enabled():
        raise AIProviderError("Gemini is not configured")

    payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}],
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json",
        },
    }

    request = Request(
        url=f"{settings.gemini_base_url.rstrip('/')}/models/{settings.gemini_model}:generateContent",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": settings.gemini_api_key or "",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.gemini_timeout_seconds) as response:
            raw_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="ignore")
        raise AIProviderError(f"Gemini request failed with status {error.code}: {error_body}") from error
    except URLError as error:
        raise AIProviderError(f"Gemini request failed: {error.reason}") from error

    candidates = raw_payload.get("candidates") or []
    if not candidates:
        raise AIProviderError("Gemini returned no candidates")

    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))

    if not text.strip():
        raise AIProviderError("Gemini returned empty content")

    try:
        return _extract_json_block(text)
    except json.JSONDecodeError as error:
        raise AIProviderError(f"Gemini returned invalid JSON: {text}") from error


def request_json_from_provider(
    *,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
) -> dict[str, Any]:
    settings = get_settings()
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        return request_json_from_gemini(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
    if provider == "kimi":
        return request_json_from_kimi(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
    raise AIProviderError(f"Unsupported LLM provider: {settings.llm_provider}")
