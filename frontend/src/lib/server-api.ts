import type { Threat, ThreatDetail, ThreatListResponse } from "@/types";

// Server-component data access. Unlike src/lib/api.ts (browser fetch with
// auth headers), these run on the server at request time and lean on Next's
// fetch cache so threat pages behave like ISR: rendered once, cached, and
// re-fetched at most hourly — new threats from the daily scrape get pages
// without a redeploy.
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const THREAT_REVALIDATE_SECONDS = 3600;

/** Fetch one threat profile. Returns null when the API says 404 so the
 *  page can render notFound(); any other failure throws (a transient API
 *  error must not get cached as a missing page). */
export async function fetchThreat(slug: string): Promise<ThreatDetail | null> {
  const res = await fetch(
    `${API_URL}/api/threats/${encodeURIComponent(slug)}`,
    { next: { revalidate: THREAT_REVALIDATE_SECONDS } },
  );
  if (res.status === 404) return null;
  if (!res.ok) {
    throw new Error(`Threat API returned ${res.status} for slug "${slug}"`);
  }
  return res.json();
}

/** Fetch every active threat (paginated), for the sitemap. Capped at 10
 *  pages of 100 as a runaway guard. */
export async function fetchAllThreats(): Promise<Threat[]> {
  const threats: Threat[] = [];
  for (let page = 1; page <= 10; page++) {
    const res = await fetch(
      `${API_URL}/api/threats?per_page=100&page=${page}`,
      { next: { revalidate: THREAT_REVALIDATE_SECONDS } },
    );
    if (!res.ok) {
      throw new Error(`Threat list API returned ${res.status}`);
    }
    const data: ThreatListResponse = await res.json();
    threats.push(...data.threats);
    if (threats.length >= data.total || data.threats.length === 0) break;
  }
  return threats;
}
