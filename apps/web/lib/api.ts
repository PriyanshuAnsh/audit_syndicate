const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function getRefreshToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("refresh_token");
}

export function setTokens(access: string, refresh: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

export function clearTokens() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

async function parseError(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") return body.detail;
    return JSON.stringify(body);
  } catch {
    return response.statusText || "request failed";
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
    cache: "no-store",
  });

  if (!response.ok) {
    clearTokens();
    return null;
  }

  const payload = await response.json();
  setTokens(payload.access_token, payload.refresh_token);
  return payload.access_token;
}

export async function api(path: string, init?: RequestInit) {
  const makeRequest = async (token?: string | null) => {
    const headers = new Headers(init?.headers || {});
    headers.set("Content-Type", "application/json");
    if (token) headers.set("Authorization", `Bearer ${token}`);

    return fetch(`${API_URL}${path}`, { ...init, headers, cache: "no-store" });
  };

  let response = await makeRequest(getToken());

  if (response.status === 401) {
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      response = await makeRequest(newAccess);
    }
  }

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}
