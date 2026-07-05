"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getDashboardStats, getDailyInsight, getThreats } from "@/lib/api";
import { DashboardStats, DailyInsight, Threat } from "@/types";
import { formatTag, typeLabel } from "@/lib/labels";

const sevStyle: Record<string, string> = {
  critical: "bg-red-50 text-red-600 border-red-200",
  high: "bg-orange-50 text-orange-600 border-orange-200",
  medium: "bg-amber-50 text-amber-600 border-amber-200",
  low: "bg-green-50 text-green-600 border-green-200",
};

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [agentThreats, setAgentThreats] = useState<Threat[]>([]);
  const [watchlist, setWatchlist] = useState<Threat[]>([]);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [insight, setInsight] = useState<DailyInsight | null>(null);

  useEffect(() => {
    getDashboardStats().then(setStats).catch(() => {
      setStats({
        critical_count: 14, high_count: 47, active_campaigns: 23, sources_monitored: 14,
        critical_delta: 3, high_delta: 8,
        agent_count: 18, agent_critical_count: 4, agent_new_week: 6, conventional_count: 12,
      });
    });
    getThreats({ page: 1, category: "agent" }).then((r) => setAgentThreats(r.threats.slice(0, 5))).catch(() => {});
    getThreats({ page: 1, category: "conventional" }).then((r) => setWatchlist(r.threats.slice(0, 5))).catch(() => {});
    getDailyInsight().then(setInsight).catch(() => {});
  }, []);

  const statCards = stats ? [
    { label: "Agent Threats Tracked", value: stats.agent_count, delta: `↑ ${stats.agent_new_week} new this week`, color: "text-purple-600", bar: "from-purple-500 to-purple-300" },
    { label: "Critical · Agent", value: stats.agent_critical_count, delta: "Highest response priority", color: "text-red-600", bar: "from-red-500 to-red-300" },
    { label: "Conventional Watchlist", value: stats.conventional_count, delta: "Secondary coverage", color: "text-blue-600", bar: "from-blue-500 to-blue-300" },
    { label: "Sources Monitored", value: stats.sources_monitored, delta: "Agent + conventional feeds", color: "text-green-600", bar: "from-green-500 to-green-300" },
  ] : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Agent Threat Dashboard</h1>
          <p className="text-sm text-gray-500 font-mono mt-1">
            {new Date().toUTCString().replace("GMT", "UTC")}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs font-mono text-green-600 uppercase tracking-wider">Live</span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s) => (
          <div key={s.label} className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm relative overflow-hidden">
            <div className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r ${s.bar}`} />
            <p className="text-[10px] font-mono uppercase tracking-widest text-gray-500 mb-1">{s.label}</p>
            <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-[11px] font-mono text-gray-500 mt-1">{s.delta}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          {/* Trending Agent Threats */}
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold flex items-center gap-2">
                <span className="text-purple-600">▲</span> Trending Agent Threats
                <span className="text-[9px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border bg-purple-50 text-purple-600 border-purple-200">Primary Feed</span>
              </h2>
              <span className="text-[10px] font-mono text-gray-400">CLICK TO EXPAND</span>
            </div>
            {agentThreats.map((t, i) => (
              <div key={t.id} className="border-b border-gray-100 last:border-0">
                <div
                  className="flex gap-3 items-start py-3 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded-lg transition-colors"
                  onClick={() => setExpanded(expanded === t.id ? null : t.id)}
                >
                  <span className="text-[10px] font-mono text-gray-400 mt-1 w-5">{String(i + 1).padStart(2, "0")}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-[10px] transition-transform ${expanded === t.id ? "rotate-90" : ""}`}>▶</span>
                      <span className="text-sm font-semibold">{t.name}</span>
                    </div>
                    <p className="text-xs text-gray-500 leading-relaxed">{t.summary}</p>
                  </div>
                  <span className={`text-[9px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border ${sevStyle[t.severity]}`}>{t.severity}</span>
                </div>
                {expanded === t.id && (
                  <div className="ml-8 mb-3 p-4 bg-purple-50/50 border border-purple-100 rounded-lg text-xs text-gray-600 leading-relaxed space-y-2">
                    <p><span className="font-mono text-[9px] uppercase tracking-wider text-purple-600">Type:</span> {typeLabel(t.threat_type)}</p>
                    <p><span className="font-mono text-[9px] uppercase tracking-wider text-purple-600">Tags:</span> {t.tags.split(",").filter(Boolean).map((tag) => formatTag(tag)).join(" · ")}</p>
                    {t.cvss_score && <p><span className="font-mono text-[9px] uppercase tracking-wider text-purple-600">CVSS:</span> {t.cvss_score}</p>}
                    <Link href={`/threats/${t.slug}`} className="inline-block mt-2 text-purple-600 font-semibold hover:underline">
                      View full profile →
                    </Link>
                  </div>
                )}
              </div>
            ))}
            {agentThreats.length === 0 && <p className="text-sm text-gray-400 py-4 text-center">Loading agent threats...</p>}
          </div>

          {/* Conventional Watchlist */}
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold flex items-center gap-2">
                <span className="text-blue-600">◆</span> Conventional Watchlist
              </h2>
              <Link href="/library?category=conventional" className="text-[10px] font-mono text-blue-600 hover:underline uppercase tracking-wider">View all →</Link>
            </div>
            {watchlist.map((t) => (
              <div key={t.id} className="flex items-center gap-3 py-2 border-b border-gray-100 last:border-0">
                <span className={`text-[9px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border shrink-0 ${sevStyle[t.severity]}`}>{t.severity}</span>
                <Link href={`/threats/${t.slug}`} className="text-xs font-medium text-gray-700 hover:text-blue-600 truncate flex-1">
                  {t.name}
                </Link>
                <span className="text-[10px] font-mono text-gray-400 shrink-0">{typeLabel(t.threat_type)}</span>
              </div>
            ))}
            {watchlist.length === 0 && <p className="text-xs text-gray-400 py-2 text-center">Loading watchlist...</p>}
          </div>
        </div>

        {/* AI Insight + Quick Links */}
        <div className="space-y-5">
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-5 shadow-sm">
            <div className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white text-[10px] font-mono font-bold tracking-wider px-2.5 py-1 rounded mb-3">AI INSIGHT</div>
            {insight?.insight ? (
              <>
                <p className="text-sm text-gray-600 leading-relaxed">{insight.insight}</p>
                <p className="text-[10px] font-mono text-gray-400 mt-3 uppercase tracking-wider">
                  Generated by {insight.model || "Gemini"}
                  {insight.generated_at ? ` · ${new Date(insight.generated_at).toUTCString().slice(0, 16)}` : ""}
                </p>
              </>
            ) : (
              <p className="text-sm text-gray-600 leading-relaxed">
                Attackers are moving up the stack: <span className="text-purple-600 font-semibold">prompt injection, tool poisoning, and compromised agent frameworks</span> now
                turn a routine agent connection into host compromise, while conventional edge-device exploits continue in the background.
              </p>
            )}
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold mb-3">Quick Links</h3>
            <div className="space-y-2">
              <Link href="/library" className="block text-sm text-purple-600 hover:underline">Browse Agent Threats →</Link>
              <Link href="/library?severity=critical" className="block text-sm text-red-600 hover:underline">View Critical Threats →</Link>
              <Link href="/library?category=conventional" className="block text-sm text-blue-600 hover:underline">Conventional Threats →</Link>
              <Link href="/pricing" className="block text-sm text-gray-600 hover:underline">Upgrade to Pro →</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
