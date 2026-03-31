const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...options.headers,
    },
    method: options.method || "GET",
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    let detail = "Request failed";
    try {
      const payload = await response.json();
      detail = payload.detail || payload.message || detail;
    } catch {
      detail = response.statusText || detail;
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  signup: (body) => request("/auth/signup", { method: "POST", body }),
  login: (body) => request("/auth/login", { method: "POST", body }),
  getProfile: (token) => request("/users/me", { token }),
  updateProfile: (token, body) =>
    request("/users/me", { method: "PUT", token, body }),
  listSkills: (token) => request("/skills/", { token }),
  listMySkills: (token) => request("/skills/me", { token }),
  createSkill: (token, body) =>
    request("/skills/", { method: "POST", token, body }),
  updateSkill: (token, skillId, body) =>
    request(`/skills/${skillId}`, { method: "PUT", token, body }),
  deleteSkill: (token, skillId) =>
    request(`/skills/${skillId}`, { method: "DELETE", token }),
  getMatches: (token) => request("/skills/matches/me", { token }),
  listExchangeRequests: (token) => request("/exchange-requests/", { token }),
  createExchangeRequest: (token, body) =>
    request("/exchange-requests/", { method: "POST", token, body }),
  updateExchangeRequestStatus: (token, requestId, body) =>
    request(`/exchange-requests/${requestId}/status`, {
      method: "PATCH",
      token,
      body,
    }),
};
