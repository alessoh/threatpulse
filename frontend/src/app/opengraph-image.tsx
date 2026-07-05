import { ImageResponse } from "next/og";

// Social-share card served at /opengraph-image and referenced automatically
// via og:image / twitter:image on every route. Rendered at build time from
// JSX — no binary asset to maintain.
export const alt = "ThreatPulse — Threat intelligence for the age of AI agents";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "80px",
          background: "linear-gradient(135deg, #0b1020 0%, #151a35 55%, #2a1a4a 100%)",
          color: "white",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <div
            style={{
              width: "64px",
              height: "64px",
              borderRadius: "14px",
              background: "linear-gradient(135deg, #2563eb, #06b6d4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "38px",
              fontWeight: 700,
            }}
          >
            T
          </div>
          <div style={{ fontSize: "44px", fontWeight: 700, letterSpacing: "-1px" }}>
            ThreatPulse
          </div>
        </div>
        <div
          style={{
            marginTop: "48px",
            fontSize: "64px",
            fontWeight: 700,
            lineHeight: 1.15,
            letterSpacing: "-2px",
            maxWidth: "980px",
          }}
        >
          Threat intelligence for the age of AI agents.
        </div>
        <div
          style={{
            marginTop: "36px",
            fontSize: "28px",
            color: "#a5b4fc",
            maxWidth: "900px",
            lineHeight: 1.4,
          }}
        >
          Prompt injection · MCP tool poisoning · agent worms · framework CVEs —
          explained in plain English, updated daily.
        </div>
      </div>
    ),
    size,
  );
}
