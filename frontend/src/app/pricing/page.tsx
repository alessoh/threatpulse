import type { Metadata } from "next";
import PricingContent from "./PricingContent";

export const metadata: Metadata = {
  title: "Pricing — ThreatPulse",
  description:
    "ThreatPulse plans: free agent-threat dashboard and library, Professional with full playbooks and unlimited AI Threat Advisor, and Enterprise with STIX API access.",
  alternates: { canonical: "/pricing" },
};

export default function PricingPage() {
  return <PricingContent />;
}
