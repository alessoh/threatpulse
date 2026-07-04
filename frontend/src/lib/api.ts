const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("tp_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}/api${path}`, { ...options, headers });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

// ── Auth ──

export async function register(email: string, password: string, full_name: string, company: string) {
  return request<import("@/types").AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, full_name, company }),
  });
}

export async function login(email: string, password: string) {
  return request<import("@/types").AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getMe() {
  return request<import("@/types").User>("/auth/me");
}

export async function updateProfile(data: Record<string, unknown>) {
  return request<import("@/types").User>("/auth/me", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// ── Dashboard ──

export async function getDashboardStats() {
  return request<import("@/types").DashboardStats>("/dashboard/stats");
}

export async function getDailyInsight() {
  return request<import("@/types").DailyInsight>("/dashboard/insight");
}

// ── Threats ──

export async function getThreats(params: {
  page?: number;
  severity?: string;
  threat_type?: string;
  search?: string;
} = {}) {
  const qs = new URLSearchParams();
  if (params.page) qs.set("page", String(params.page));
  if (params.severity) qs.set("severity", params.severity);
  if (params.threat_type) qs.set("threat_type", params.threat_type);
  if (params.search) qs.set("search", params.search);
  return request<import("@/types").ThreatListResponse>(`/threats?${qs}`);
}

export async function getThreat(slug: string) {
  return request<import("@/types").ThreatDetail>(`/threats/${slug}`);
}

export async function getPlaybook(slug: string) {
  return request<import("@/types").Playbook>(`/threats/${slug}/playbook`);
}

// ── AI ──

export async function askAdvisor(message: string, threatId?: number, history: object[] = []) {
  return request<{ response: string }>("/advisor", {
    method: "POST",
    body: JSON.stringify({ message, threat_id: threatId, conversation_history: history }),
  });
}

export async function aiSearch(query: string) {
  return request<{ results: unknown[]; source: string }>(`/search?q=${encodeURIComponent(query)}`);
}

// ── Bookmarks ──

export async function addBookmark(threatId: number) {
  return request<{ status: string }>(`/bookmarks/${threatId}`, { method: "POST" });
}

export async function removeBookmark(threatId: number) {
  return request<{ status: string }>(`/bookmarks/${threatId}`, { method: "DELETE" });
}

export async function getBookmarks() {
  return request<import("@/types").Threat[]>("/bookmarks");
}

// ── Subscriptions ──

export async function createCheckout(priceId: string) {
  return request<{ checkout_url: string }>("/subscribe/checkout", {
    method: "POST",
    body: JSON.stringify({ price_id: priceId }),
  });
}

export async function createPortal() {
  return request<{ portal_url: string }>("/subscribe/portal", { method: "POST" });
}
