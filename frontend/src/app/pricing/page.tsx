"use client";
import { useAuth } from "@/lib/auth";
import { createCheckout, createPortal } from "@/lib/api";

const plans = [
  {
    name: "Free", price: "$0", period: "", desc: "Essential threat awareness for individuals and small teams.",
    btnLabel: "Get Started Free", btnStyle: "border border-gray-200 text-gray-800 hover:border-blue-500 hover:text-blue-600",
    featured: false, checkColor: "text-green-600", priceId: null,
    features: ["Global threat dashboard", "Top 10 trending threats", "Executive summaries", "Basic remediation checklists", "Weekly threat digest email"],
  },
  {
    name: "Professional", price: "$39", period: "/mo", desc: "Full threat intelligence for security teams and IT professionals.",
    btnLabel: "Start Pro Trial", btnStyle: "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md hover:shadow-lg",
    featured: true, checkColor: "text-blue-600", priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_PRO || "",
    features: ["Everything in Free", "Full threat profiles & IOCs", "Complete remediation playbooks", "AI Threat Advisor (unlimited)", "Sector-specific briefings", "Real-time email alerts", "Custom alert filters"],
  },
  {
    name: "Enterprise", price: "$199", period: "/mo", desc: "Full platform access with API integration for SOCs.",
    btnLabel: "Contact Sales", btnStyle: "bg-gray-100 border border-gray-200 text-gray-800 hover:border-purple-400 hover:text-purple-600",
    featured: false, checkColor: "text-purple-600", priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_ENTERPRISE || "",
    features: ["Everything in Professional", "REST API access (STIX format)", "SIEM integration guides", "Custom threat reports", "Priority alerting (15-min SLA)", "Dedicated account manager", "Team seats (up to 25)"],
  },
];

const comparison = [
  { feature: "Global threat dashboard", free: "✓", pro: "✓", ent: "✓" },
  { feature: "Threat profiles", free: "Summary", pro: "Full + IOCs", ent: "Full + IOCs" },
  { feature: "Remediation playbooks", free: "Checklists", pro: "Full playbooks", ent: "Full + custom" },
  { feature: "AI Threat Advisor", free: "3/day", pro: "Unlimited", ent: "Unlimited+" },
  { feature: "Email alerts", free: "Weekly", pro: "Real-time", ent: "Priority 15m" },
  { feature: "Sector briefings", free: "—", pro: "✓", ent: "✓" },
  { feature: "API access", free: "—", pro: "—", ent: "REST + STIX" },
  { feature: "SIEM integration", free: "—", pro: "—", ent: "✓" },
  { feature: "Team seats", free: "1", pro: "5", ent: "25" },
  { feature: "Support", free: "Community", pro: "Email", ent: "Dedicated" },
];

export default function PricingPage() {
  const { user } = useAuth();

  async function handleSubscribe(priceId: string | null) {
    if (!priceId) return;
    if (!user) { alert("Please sign in first."); return; }
    if (user.tier === "pro" || user.tier === "enterprise") {
      try {
        const res = await createPortal();
        window.location.href = res.portal_url;
      } catch { alert("Unable to open billing portal."); }
      return;
    }
    try {
      const res = await createCheckout(priceId);
      window.location.href = res.checkout_url;
    } catch (e: any) { alert(e.message || "Checkout failed."); }
  }

  return (
    <div className="space-y-12 max-w-5xl mx-auto">
      {/* Hero */}
      <div className="text-center pt-6">
        <div className="inline-flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-full px-4 py-1.5 mb-5">
          <span className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
          <span className="text-[11px] font-mono text-blue-600 tracking-wider">Now in Early Access</span>
        </div>
        <h1 className="text-4xl font-bold leading-tight mb-4">
          Threat intelligence that<br />
          <span className="bg-gradient-to-r from-blue-600 via-cyan-500 to-purple-600 bg-clip-text text-transparent">actually fits your team</span>
        </h1>
        <p className="text-gray-500 max-w-lg mx-auto leading-relaxed">
          From free threat awareness to enterprise-grade intelligence feeds. Choose the depth of insight your organization needs.
        </p>
      </div>

      {/* Plans */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {plans.map((p) => (
          <div key={p.name} className={`bg-white rounded-2xl p-7 flex flex-col relative transition-all hover:-translate-y-1 hover:shadow-lg ${
            p.featured ? "border-2 border-blue-500 shadow-md" : "border border-gray-200 shadow-sm"
          }`}>
            {p.featured && (
              <>
                <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-600 via-cyan-500 to-purple-600 rounded-t-2xl" />
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-[10px] font-mono font-bold tracking-widest uppercase px-3.5 py-1 rounded-full">Most Popular</div>
              </>
            )}
            <p className="text-xs font-mono uppercase tracking-widest text-gray-500 mb-1">{p.name}</p>
            <p className="text-4xl font-bold mb-1">{p.price}<span className="text-base font-normal text-gray-400">{p.period}</span></p>
            <p className="text-sm text-gray-500 mb-5">{p.desc}</p>
            <div className="h-px bg-gray-200 mb-5" />
            <ul className="flex-1 space-y-2.5 mb-6">
              {p.features.map((f) => (
                <li key={f} className="flex gap-2.5 items-start text-sm text-gray-600">
                  <span className={`font-bold ${p.checkColor} mt-0.5`}>✓</span> {f}
                </li>
              ))}
            </ul>
            <button onClick={() => handleSubscribe(p.priceId)}
              className={`w-full py-3 rounded-xl font-semibold transition-all ${p.btnStyle}`}>
              {user && (user.tier === "pro" || user.tier === "enterprise") ? "Manage Subscription" : p.btnLabel}
            </button>
          </div>
        ))}
      </div>

      {/* Comparison */}
      <div>
        <h2 className="text-xl font-bold text-center mb-2">Detailed Feature Comparison</h2>
        <p className="text-sm text-gray-500 text-center mb-6">Everything you need to choose the right plan</p>
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-left p-3 font-mono text-[11px] uppercase tracking-wider text-gray-500">Feature</th>
                <th className="text-left p-3 font-mono text-[11px] uppercase tracking-wider text-gray-500">Free</th>
                <th className="text-left p-3 font-mono text-[11px] uppercase tracking-wider text-gray-500">Pro</th>
                <th className="text-left p-3 font-mono text-[11px] uppercase tracking-wider text-gray-500">Enterprise</th>
              </tr>
            </thead>
            <tbody>
              {comparison.map((r) => (
                <tr key={r.feature} className="border-t border-gray-100">
                  <td className="p-3 font-medium text-gray-800">{r.feature}</td>
                  <td className="p-3">{r.free === "✓" ? <span className="text-green-600 font-bold">✓</span> : r.free === "—" ? <span className="text-gray-300">—</span> : <span className="font-mono text-[11px] text-blue-600">{r.free}</span>}</td>
                  <td className="p-3">{r.pro === "✓" ? <span className="text-green-600 font-bold">✓</span> : r.pro === "—" ? <span className="text-gray-300">—</span> : <span className="font-mono text-[11px] text-blue-600">{r.pro}</span>}</td>
                  <td className="p-3">{r.ent === "✓" ? <span className="text-green-600 font-bold">✓</span> : r.ent === "—" ? <span className="text-gray-300">—</span> : <span className="font-mono text-[11px] text-blue-600">{r.ent}</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer */}
      <p className="text-center text-xs font-mono text-gray-400 pb-8">
        ThreatPulse — AI-Powered Cyber Threat Intelligence
      </p>
    </div>
  );
}
