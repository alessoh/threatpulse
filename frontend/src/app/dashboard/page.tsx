import type { Metadata } from "next";
import DashboardContent from "./DashboardContent";

export const metadata: Metadata = {
  title: "Agent Threat Dashboard — ThreatPulse",
  description:
    "Live dashboard of threats to AI agents: trending agent threats, a conventional watchlist, agent-focused stats, and a daily AI-written landscape briefing.",
  alternates: { canonical: "/dashboard" },
};

export default function DashboardPage() {
  return <DashboardContent />;
}
