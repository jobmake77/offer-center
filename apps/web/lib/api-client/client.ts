import { Envelope } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

async function buildApiError(response: Response): Promise<Error> {
  let fallbackMessage = `Request failed with status ${response.status}.`;

  try {
    const payload = await response.json();

    if (typeof payload?.error === "string" && payload.error) {
      return new Error(payload.error);
    }

    if (typeof payload?.error?.message === "string" && payload.error.message) {
      return new Error(payload.error.message);
    }

    if (typeof payload?.detail === "string" && payload.detail) {
      return new Error(payload.detail);
    }

    if (Array.isArray(payload?.detail) && payload.detail.length > 0) {
      const message = payload.detail
        .map((item: { msg?: string }) => item.msg)
        .filter(Boolean)
        .join(", ");

      if (message) {
        return new Error(message);
      }
    }
  } catch {
    if (response.status === 500) {
      fallbackMessage = "The server hit an unexpected error. Please try again.";
    }
  }

  return new Error(fallbackMessage);
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw await buildApiError(response);
  }

  const payload = (await response.json()) as Envelope<T>;
  return payload.data;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body),
    cache: "no-store"
  });

  if (!response.ok) {
    throw await buildApiError(response);
  }

  const payload = (await response.json()) as Envelope<T>;
  return payload.data;
}

export async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body),
    cache: "no-store"
  });

  if (!response.ok) {
    throw await buildApiError(response);
  }

  const payload = (await response.json()) as Envelope<T>;
  return payload.data;
}

export async function apiPostFormData<T>(path: string, formData: FormData): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
    cache: "no-store"
  });

  if (!response.ok) {
    throw await buildApiError(response);
  }

  const payload = (await response.json()) as Envelope<T>;
  return payload.data;
}

export async function safeApiGet<T>(path: string, fallback: T): Promise<T> {
  try {
    return await apiGet<T>(path);
  } catch {
    return fallback;
  }
}
