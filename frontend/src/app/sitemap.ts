import type { MetadataRoute } from "next";
import { fetchAllThreats } from "@/lib/server-api";

const BASE = "https://threatpulse.dev";

// Served at /sitemap.xml. Static routes plus one URL per threat profile.
// The threat list is fetched with an hourly revalidate, so pages created by
// the daily scrape appear here without a redeploy. If the API is
// unreachable (e.g. during an isolated build), fall back to the static
// routes rather than failing the build.
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticRoutes: MetadataRoute.Sitemap = [
    { url: `${BASE}/`, changeFrequency: "weekly", priority: 1 },
    { url: `${BASE}/dashboard`, changeFrequency: "daily", priority: 0.9 },
    { url: `${BASE}/library`, changeFrequency: "daily", priority: 0.9 },
    { url: `${BASE}/pricing`, changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE}/terms`, changeFrequency: "yearly", priority: 0.2 },
  ];

  let threatRoutes: MetadataRoute.Sitemap = [];
  try {
    const threats = await fetchAllThreats();
    threatRoutes = threats.map((t) => ({
      url: `${BASE}/threats/${encodeURIComponent(t.slug)}`,
      lastModified: t.last_updated,
      changeFrequency: "weekly" as const,
      priority: 0.8,
    }));
  } catch (err) {
    console.error("[sitemap] threat list unavailable, serving static routes only:", err);
  }

  return [...staticRoutes, ...threatRoutes];
}
