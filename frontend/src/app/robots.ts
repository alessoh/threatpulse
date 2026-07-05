import type { MetadataRoute } from "next";

// Served at /robots.txt. Everything is crawlable today; when per-threat
// pages ship, revisit whether the client-rendered app shells (/dashboard,
// /library) should be de-prioritized in favor of the server-rendered
// threat pages.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: "https://threatpulse.dev/sitemap.xml",
  };
}
