import type { Metadata } from "next";
import { Suspense } from "react";
import LibraryContent from "./LibraryContent";

export const metadata: Metadata = {
  title: "Threat Library — ThreatPulse",
  description:
    "Searchable catalog of AI-agent and conventional cyber threats: prompt injection, MCP tool poisoning, memory poisoning, agent worms, and framework CVEs — with severity, tags, and remediation.",
  // One canonical for the library regardless of ?category/?severity/?search
  // query-parameter variants.
  alternates: { canonical: "/library" },
};

export default function LibraryPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-gray-400">Loading threat library...</div>}>
      <LibraryContent />
    </Suspense>
  );
}
