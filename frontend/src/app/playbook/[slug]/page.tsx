"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getThreat, askAdvisor } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ThreatDetail } from "@/types";

interface ChatMsg { role: "system" | "user" | "assistant"; content: string }

export default function PlaybookPage() {
  const { slug } = useParams<{ slug: string }>();
  const { user } = useAuth();
  const [threat, setThreat] = useState<ThreatDetail | null>(null);
  const [msgs, setMsgs] = useState<ChatMsg[]>([{ role: "system", content: "I'm your AI Threat Advisor. Ask me anything about this threat, remediation steps, or how it affects your environment." }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const isPro = user && (user.tier === "pro" || user.tier === "enterprise");

  useEffect(() => { if (slug) getThreat(slug).then(setThreat).catch(() => {}); }, [slug]);

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const q = input.trim();
    setInput("");
    setMsgs((m) => [...m, { role: "user", content: q }]);
    setLoading(true);

    try {
      const history = msgs.filter((m) => m.role !== "system").map((m) => ({ role: m.role, content: m.content }));
      const res = await askAdvisor(q, threat?.id, history);
      setMsgs((m) => [...m, { role: "assistant", content: res.response }]);
    } catch {
      setMsgs((m) => [...m, { role: "assistant", content: "Unable to reach the AI advisor. Please try again." }]);
    }
    setLoading(false);
  }

  if (!threat) return <div className="text-center py-20 text-gray-400">Loading threat profile...</div>;

  let steps: { title: string; description: string }[] = [];
  try { steps = JSON.parse(threat.remediation_steps); } catch { steps = []; }

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="bg-white border border-gray-200 rounded-2xl p-7 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-red-500 to-orange-400" />
        <p className="text-[10px] font-mono text-gray-400 uppercase tracking-widest mb-3">
          Threat Library <span className="text-blue-500">›</span> {threat.threat_type} <span className="text-blue-500">›</span> {threat.name}
        </p>
        <div className="flex items-start gap-3 flex-wrap mb-3">
          <h1 className="text-2xl font-bold leading-tight">{threat.name}<br />Remediation Playbook</h1>
          <span className="text-[10px] font-mono uppercase tracking-wider px-2.5 py-1 rounded-md bg-red-50 text-red-600 border border-red-200 font-semibold">{threat.severity}</span>
        </div>
        <div className="flex gap-5 flex-wrap font-mono text-[11px] text-gray-500">
          <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-red-500" /> Actively Exploited</span>
          {threat.cvss_score && <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-amber-500" /> CVSS {threat.cvss_score}</span>}
          <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-500" /> Updated {new Date(threat.last_updated).toLocaleDateString()}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Playbook Content */}
        <div className="lg:col-span-2 space-y-0">
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
            {/* Executive Summary - FREE */}
            <div className="p-6 border-b border-gray-100">
              <p className="text-[10px] font-mono text-blue-600 uppercase tracking-widest mb-1 flex items-center gap-2">Section 01 <span className="flex-1 h-px bg-gray-200" /></p>
              <h2 className="text-lg font-semibold mb-3">Executive Summary</h2>
              <p className="text-sm text-gray-600 leading-relaxed">{threat.summary}</p>
            </div>

            {/* Technical Analysis - FREE */}
            <div className="p-6 border-b border-gray-100">
              <p className="text-[10px] font-mono text-blue-600 uppercase tracking-widest mb-1 flex items-center gap-2">Section 02 <span className="flex-1 h-px bg-gray-200" /></p>
              <h2 className="text-lg font-semibold mb-3">Technical Analysis</h2>
              <p className="text-sm text-gray-600 leading-relaxed">{threat.technical_analysis}</p>
              {threat.iocs && (
                <div className="mt-4 bg-gray-50 border border-gray-200 rounded-lg p-4 font-mono text-[11px] text-gray-700 whitespace-pre-wrap">{threat.iocs}</div>
              )}
            </div>

            {/* Remediation - GATED */}
            <div className="p-6 relative">
              <p className="text-[10px] font-mono text-blue-600 uppercase tracking-widest mb-1 flex items-center gap-2">Section 03 <span className="flex-1 h-px bg-gray-200" /></p>
              <h2 className="text-lg font-semibold mb-3">Step-by-Step Remediation</h2>

              {isPro ? (
                <div className="space-y-3">
                  {steps.map((s, i) => (
                    <div key={i} className="flex gap-3">
                      <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-600 to-cyan-500 text-white text-[10px] font-mono font-bold flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</div>
                      <div>
                        <p className="font-semibold text-sm">{s.title}</p>
                        <p className="text-sm text-gray-500 leading-relaxed">{s.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="relative">
                  <div className="blur-sm select-none pointer-events-none opacity-60 space-y-3">
                    {steps.slice(0, 4).map((s, i) => (
                      <div key={i} className="flex gap-3">
                        <div className="w-6 h-6 rounded-full bg-blue-500 text-white text-[10px] flex items-center justify-center flex-shrink-0">{i + 1}</div>
                        <div><p className="font-semibold text-sm">{s.title}</p><p className="text-sm text-gray-500">{s.description}</p></div>
                      </div>
                    ))}
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/80 to-white flex flex-col items-center justify-center text-center px-8">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white text-xl mb-3 shadow-lg">🔒</div>
                    <h3 className="text-lg font-bold mb-1">Full Playbook Access</h3>
                    <p className="text-sm text-gray-500 mb-4 max-w-xs">Complete remediation steps, YARA rules, and configuration templates require a Pro subscription.</p>
                    <Link href="/pricing" className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2.5 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all">
                      Unlock with Pro
                    </Link>
                    <p className="text-[11px] font-mono text-gray-400 mt-2">$39/month. Cancel anytime.</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* AI Advisor */}
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm flex flex-col max-h-[700px] sticky top-20">
          <div className="p-4 border-b border-gray-100 flex items-center gap-2">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-[10px] font-mono font-bold tracking-wider px-2 py-0.5 rounded">AI</span>
            <span className="text-sm font-semibold">Threat Advisor</span>
            {user && <span className="ml-auto text-[9px] font-mono text-green-600 bg-green-50 border border-green-200 px-2 py-0.5 rounded">LIVE</span>}
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-2.5 min-h-[300px]">
            {msgs.map((m, i) => (
              <div key={i} className={`max-w-[90%] px-3 py-2.5 rounded-xl text-[13px] leading-relaxed whitespace-pre-wrap ${
                m.role === "system" ? "bg-blue-50 border border-blue-100 text-gray-600 self-start" :
                m.role === "user" ? "bg-blue-600 text-white self-end ml-auto rounded-br-sm" :
                "bg-gray-100 border border-gray-200 text-gray-600 self-start"
              }`}>{m.content}</div>
            ))}
            {loading && <div className="text-xs text-gray-400 italic">Analyzing...</div>}
          </div>

          <div className="p-3 border-t border-gray-100 flex gap-2">
            <input
              type="text" value={input} onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder={user ? "Ask about this threat..." : "Sign in to use AI advisor"}
              disabled={!user || loading}
              className="flex-1 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 disabled:opacity-50"
            />
            <button onClick={sendMessage} disabled={!user || loading}
              className="bg-blue-600 text-white rounded-lg px-4 py-2 font-mono text-[11px] font-semibold disabled:opacity-40">
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
