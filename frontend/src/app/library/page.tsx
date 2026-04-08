"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { getThreats, aiSearch } from "@/lib/api";
import { Threat } from "@/types";

const sevStyle: Record<string, string> = {
  critical: "bg-red-50 text-red-600 border-red-200",
  high: "bg-orange-50 text-orange-600 border-orange-200",
  medium: "bg-amber-50 text-amber-600 border-amber-200",
  low: "bg-green-50 text-green-600 border-green-200",
};

const sevBar: Record<string, string> = {
  critical: "bg-red-500", high: "bg-orange-500", medium: "bg-amber-500", low: "bg-green-500",
};

const typeFilters = ["all", "ransomware", "apt", "zero-day", "supply-chain", "phishing"];
const sevFilters = ["all", "critical", "high", "medium"];

export default function LibraryPage() {
  const params = useSearchParams();
  const [threats, setThreats] = useState<Threat[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [typeFilter, setTypeFilter] = useState("all");
  const [sevFilter, setSevFilter] = useState(params.get("severity") || "all");
  const [search, setSearch] = useState(params.get("search") || "");
  const [expanded, setExpanded] = useState<number | null>(null);
  const [aiResult, setAiResult] = useState<any>(null);
  const [searching, setSearching] = useState(false);

  useEffect(() => { fetchThreats(); }, [page, typeFilter, sevFilter]);

  function fetchThreats() {
    const p: any = { page };
    if (typeFilter !== "all") p.threat_type = typeFilter;
    if (sevFilter !== "all") p.severity = sevFilter;
    getThreats(p).then((r) => { setThreats(r.threats); setTotal(r.total); }).catch(() => {});
  }

  async function handleSearch() {
    if (!search.trim()) return;
    setSearching(true);
    setAiResult(null);
    try {
      const r = await aiSearch(search);
      setAiResult(r);
    } catch { setAiResult({ source: "error", results: [] }); }
    setSearching(false);
  }

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold">Threat Library</h1>

      {/* Search */}
      <div className="bg-white border border-gray-200 rounded-xl p-1.5 pl-5 flex gap-2 shadow-sm focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
        <input
          type="text" value={search} onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="Search threats... e.g. 'healthcare ransomware' or 'CVE-2025'"
          className="flex-1 outline-none text-sm py-2.5"
        />
        <button onClick={handleSearch} disabled={searching}
          className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-mono text-xs font-semibold tracking-wider uppercase px-5 py-2.5 rounded-lg disabled:opacity-40">
          {searching ? "Searching..." : "⟐ AI Search"}
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap items-center">
        <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider mr-1">Type</span>
        {typeFilters.map((f) => (
          <button key={f} onClick={() => { setTypeFilter(f); setPage(1); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all border ${typeFilter === f ? "bg-blue-50 border-blue-500 text-blue-600 font-medium" : "bg-white border-gray-200 text-gray-500 hover:border-blue-300"}`}>
            {f === "apt" ? "APT" : f === "zero-day" ? "Zero-Day" : f === "supply-chain" ? "Supply Chain" : f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
        <div className="w-px h-6 bg-gray-200 mx-2" />
        <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider mr-1">Severity</span>
        {sevFilters.map((f) => (
          <button key={f} onClick={() => { setSevFilter(f); setPage(1); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all border ${sevFilter === f ? "bg-blue-50 border-blue-500 text-blue-600 font-medium" : "bg-white border-gray-200 text-gray-500 hover:border-blue-300"}`}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      <p className="text-xs font-mono text-gray-400">Showing {threats.length} of {total} threats</p>

      {/* AI Result */}
      {aiResult && aiResult.results && aiResult.results.length > 0 && (
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-5 shadow-sm">
          <div className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white text-[10px] font-mono font-bold tracking-wider px-2.5 py-1 rounded mb-3">⟐ AI SEARCH RESULT</div>
          <p className="text-sm text-gray-600 leading-relaxed">{JSON.stringify(aiResult.results[0], null, 2)}</p>
        </div>
      )}

      {/* Threat Cards */}
      <div className="space-y-3">
        {threats.map((t) => (
          <div key={t.id} className="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:border-gray-300 transition-all overflow-hidden">
            <div className="flex gap-3 p-4 cursor-pointer" onClick={() => setExpanded(expanded === t.id ? null : t.id)}>
              <div className={`w-1 self-stretch rounded-full ${sevBar[t.severity]}`} />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span className="font-semibold">{t.name}</span>
                  <span className={`text-[9px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border ${sevStyle[t.severity]}`}>{t.severity}</span>
                </div>
                <div className="flex gap-1.5 mb-2 flex-wrap">
                  {t.tags.split(",").filter(Boolean).map((tag) => (
                    <span key={tag} className="text-[10px] font-mono px-2 py-0.5 bg-gray-100 rounded text-gray-500">{tag.trim()}</span>
                  ))}
                </div>
                <p className="text-sm text-gray-500 leading-relaxed">{t.summary}</p>
              </div>
              <span className={`text-gray-400 transition-transform text-lg ${expanded === t.id ? "rotate-180" : ""}`}>▾</span>
            </div>

            {expanded === t.id && (
              <div className="border-t border-gray-100 p-4 ml-7 space-y-3">
                <p className="text-xs text-gray-500">
                  <span className="font-mono text-[9px] uppercase tracking-wider text-blue-600 mr-2">Type:</span>{t.threat_type}
                  {t.cvss_score && <> · <span className="font-mono text-[9px] uppercase tracking-wider text-blue-600 mr-2">CVSS:</span>{t.cvss_score}</>}
                </p>
                <Link href={`/playbook/${t.slug}`} className="inline-block text-sm text-blue-600 font-semibold hover:underline">
                  View Full Playbook →
                </Link>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Pagination */}
      {total > 20 && (
        <div className="flex justify-center gap-2 pt-4">
          <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page <= 1}
            className="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-30">← Prev</button>
          <span className="px-3 py-1.5 text-sm text-gray-500">Page {page}</span>
          <button onClick={() => setPage(page + 1)} disabled={threats.length < 20}
            className="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-30">Next →</button>
        </div>
      )}
    </div>
  );
}
