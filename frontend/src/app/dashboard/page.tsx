"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getDashboardStats, getThreats } from "@/lib/api";
import { DashboardStats, Threat } from "@/types";

const sevStyle: Record<string, string> = {
  critical: "bg-red-50 text-red-600 border-red-200",
  high: "bg-orange-50 text-orange-600 border-orange-200",
  medium: "bg-amber-50 text-amber-600 border-amber-200",
  low: "bg-green-50 text-green-600 border-green-200",
};

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [threats, setThreats] = useState<Threat[]>([]);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    getDashboardStats().then(setStats).catch(() => {
      setStats({ critical_count: 14, high_count: 47, active_campaigns: 23, sources_monitored: 86, critical_delta: 3, high_delta: 8 });
    });
    getThreats({ page: 1 }).then((r) => setThreats(r.threats.slice(0, 5))).catch(() => {});
  }, []);

  const statCards = stats ? [
    { label: "Critical Threats", value: stats.critical_count, delta: `↑ ${stats.critical_delta} from last week`, color: "text-red-600", bar: "from-red-500 to-red-300" },
    { label: "High Severity", value: stats.high_count, delta: `↑ ${stats.high_delta} from last week`, color: "text-orange-500", bar: "from-orange-500 to-orange-300" },
    { label: "Active Campaigns", value: stats.active_campaigns, delta: "Updated in last 7d", color: "text-blue-600", bar: "from-blue-500 to-blue-300" },
    { label: "Sources Monitored", value: stats.sources_monitored, delta: "Across 14 feeds", color: "text-green-600", bar: "from-green-500 to-green-300" },
  ] : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Threat Dashboard</h1>
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
            <p className="text-[11px] font-mono text-red-500 mt-1">{s.delta}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Trending Threats */}
        <div className="lg:col-span-2 bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold flex items-center gap-2">
              <span className="text-blue-600">▲</span> Trending Threats
            </h2>
            <span className="text-[10px] font-mono text-gray-400">CLICK TO EXPAND</span>
          </div>
          {threats.map((t, i) => (
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
                <div className="ml-8 mb-3 p-4 bg-blue-50/50 border border-blue-100 rounded-lg text-xs text-gray-600 leading-relaxed space-y-2">
                  <p><span className="font-mono text-[9px] uppercase tracking-wider text-blue-600">Type:</span> {t.threat_type}</p>
                  <p><span className="font-mono text-[9px] uppercase tracking-wider text-blue-600">Tags:</span> {t.tags}</p>
                  {t.cvss_score && <p><span className="font-mono text-[9px] uppercase tracking-wider text-blue-600">CVSS:</span> {t.cvss_score}</p>}
                  <Link href={`/library?search=${encodeURIComponent(t.name)}`} className="inline-block mt-2 text-blue-600 font-semibold hover:underline">
                    View full profile →
                  </Link>
                </div>
              )}
            </div>
          ))}
          {threats.length === 0 && <p className="text-sm text-gray-400 py-4 text-center">Loading threats...</p>}
        </div>

        {/* AI Insight + Quick Links */}
        <div className="space-y-5">
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-5 shadow-sm">
            <div className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white text-[10px] font-mono font-bold tracking-wider px-2.5 py-1 rounded mb-3">AI INSIGHT</div>
            <p className="text-sm text-gray-600 leading-relaxed">
              The global threat landscape is dominated by <span className="text-blue-600 font-semibold">ransomware groups exploiting unpatched edge devices</span> within hours of disclosure.
              AI-generated phishing is compressing the window between vulnerability disclosure and mass exploitation to under 48 hours.
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold mb-3">Quick Links</h3>
            <div className="space-y-2">
              <Link href="/library" className="block text-sm text-blue-600 hover:underline">Browse Threat Library →</Link>
              <Link href="/library?severity=critical" className="block text-sm text-red-600 hover:underline">View Critical Threats →</Link>
              <Link href="/pricing" className="block text-sm text-purple-600 hover:underline">Upgrade to Pro →</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
