import type { MetadataRoute } from "next";

const BASE = "https://threatpulse.dev";

// Served at /sitemap.xml. Static routes only for now — when server-rendered
// /threats/[slug] pages ship, fetch the threat list from the API here so
// every profile is listed and picked up as the daily scrape adds new ones.
export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${BASE}/`, changeFrequency: "weekly", priority: 1 },
    { url: `${BASE}/dashboard`, changeFrequency: "daily", priority: 0.9 },
    { url: `${BASE}/library`, changeFrequency: "daily", priority: 0.9 },
    { url: `${BASE}/pricing`, changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE}/terms`, changeFrequency: "yearly", priority: 0.2 },
  ];
}
