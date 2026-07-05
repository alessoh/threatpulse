import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

const features = [
  {
    title: "Agent threats first",
    body:
      "Prompt injection, MCP tool poisoning, memory poisoning, agent worms, and framework CVEs — classified against the OWASP Agentic Top 10 with attack-surface and propagation tags.",
    accent: "from-purple-500 to-purple-300",
  },
  {
    title: "Plain English, written by AI",
    body:
      "Claude turns every raw advisory into a readable threat profile with severity and remediation steps. Gemini writes a daily briefing of what actually matters this week.",
    accent: "from-blue-500 to-blue-300",
  },
  {
    title: "From alert to action",
    body:
      "On-demand incident-response playbooks for every threat, plus a chat advisor that specializes in securing AI agent deployments. Conventional CVEs stay on the watchlist too.",
    accent: "from-green-500 to-green-300",
  },
];

const sources = [
  "GitHub Security Advisories", "NVD", "CISA KEV", "arXiv cs.CR",
  "OWASP GenAI", "Security researcher feeds",
];

export default function Home() {
  return (
    <div className="py-10 space-y-14">
      {/* Hero */}
      <div className="max-w-3xl mx-auto text-center space-y-6">
        <div className="inline-flex items-center gap-2 border border-purple-200 bg-purple-50 rounded-full px-3 py-1">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-[11px] font-mono uppercase tracking-wider text-purple-700">Live feed · updated daily</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
          Threat intelligence for the age of{" "}
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">AI agents</span>.
        </h1>
        <p className="text-lg text-gray-600 leading-relaxed">
          AI agents now browse, code, pay, and talk to each other — and attackers have followed them there.
          ThreatPulse tracks the threats aimed at agents and the pathways between them, explains each one in
          plain English, and tells you what to do about it. Conventional vulnerabilities included, one click away.
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <Link href="/dashboard"
            className="px-6 py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90 transition-opacity shadow-sm">
            Open the live dashboard →
          </Link>
          <Link href="/library"
            className="px-6 py-3 rounded-xl text-sm font-semibold text-gray-700 bg-white border border-gray-200 hover:border-purple-300 transition-colors shadow-sm">
            Browse agent threats
          </Link>
        </div>
      </div>

      {/* Feature cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl mx-auto">
        {features.map((f) => (
          <div key={f.title} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm relative overflow-hidden">
            <div className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r ${f.accent}`} />
            <h3 className="text-sm font-semibold mb-2">{f.title}</h3>
            <p className="text-sm text-gray-500 leading-relaxed">{f.body}</p>
          </div>
        ))}
      </div>

      {/* Sources strip */}
      <div className="max-w-3xl mx-auto text-center space-y-3">
        <p className="text-[10px] font-mono uppercase tracking-widest text-gray-400">Continuously monitoring</p>
        <div className="flex flex-wrap justify-center gap-2">
          {sources.map((s) => (
            <span key={s} className="text-xs font-mono px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-gray-500">{s}</span>
          ))}
        </div>
        <p className="text-sm text-gray-500 pt-2">
          Deduplicated at ingestion, synthesized by Claude, briefed daily by Gemini —{" "}
          <Link href="/pricing" className="text-purple-600 font-medium hover:underline">free to start</Link>.
        </p>
      </div>
    </div>
  );
}
