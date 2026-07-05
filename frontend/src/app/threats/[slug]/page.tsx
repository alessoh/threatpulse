import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchThreat } from "@/lib/server-api";
import { formatTag, typeLabel } from "@/lib/labels";
import type { ThreatDetail } from "@/types";

// ISR: rendered on first request, cached, re-fetched at most hourly — so
// threats added by the daily scrape get indexable pages without a redeploy.
export const revalidate = 3600;

const sevStyle: Record<string, string> = {
  critical: "bg-red-50 text-red-600 border-red-200",
  high: "bg-orange-50 text-orange-600 border-orange-200",
  medium: "bg-amber-50 text-amber-600 border-amber-200",
  low: "bg-green-50 text-green-600 border-green-200",
};

interface Step {
  title: string;
  description: string;
}

function parseSteps(raw: string): Step[] {
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((s) => s && typeof s === "object")
      .map((s) => ({ title: String(s.title ?? ""), description: String(s.description ?? "") }))
      .filter((s) => s.title || s.description);
  } catch {
    return [];
  }
}

function metaDescription(t: ThreatDetail): string {
  const base = (t.summary || "").replace(/\s+/g, " ").trim();
  if (base.length <= 155) return base;
  return `${base.slice(0, 152).replace(/\s+\S*$/, "")}…`;
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

function splitList(raw: string, separator: RegExp): string[] {
  return raw.split(separator).map((s) => s.trim()).filter(Boolean);
}

type Params = { params: { slug: string } };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const threat = await fetchThreat(params.slug);
  if (!threat) {
    return { title: "Threat not found — ThreatPulse", robots: { index: false } };
  }
  const description = metaDescription(threat);
  const path = `/threats/${threat.slug}`;
  return {
    title: `${threat.name} — ThreatPulse`,
    description,
    alternates: { canonical: path },
    openGraph: {
      type: "article",
      url: path,
      title: threat.name,
      description,
      publishedTime: threat.first_seen,
      modifiedTime: threat.last_updated,
    },
    twitter: {
      card: "summary_large_image",
      title: threat.name,
      description,
    },
  };
}

export default async function ThreatPage({ params }: Params) {
  const threat = await fetchThreat(params.slug);
  if (!threat) notFound();

  const steps = parseSteps(threat.remediation_steps);
  const tags = splitList(threat.tags, /,/);
  const cves = splitList(threat.cve_ids, /,/);
  const industries = splitList(threat.industries_affected, /,/);
  const sources = splitList(threat.source_urls, /[,\n]/).filter((s) => s.startsWith("http"));
  const iocLines = splitList(threat.iocs, /\n/);
  const isAgent = threat.category === "agent";

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "TechArticle",
        headline: threat.name,
        description: metaDescription(threat),
        datePublished: threat.first_seen,
        dateModified: threat.last_updated,
        mainEntityOfPage: `https://threatpulse.dev/threats/${threat.slug}`,
        author: { "@id": "https://threatpulse.dev/#organization" },
        publisher: { "@id": "https://threatpulse.dev/#organization" },
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: "https://threatpulse.dev/" },
          { "@type": "ListItem", position: 2, name: "Threat Library", item: "https://threatpulse.dev/library" },
          { "@type": "ListItem", position: 3, name: threat.name },
        ],
      },
    ],
  };

  return (
    <div className="max-w-3xl mx-auto py-8 space-y-5">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* Breadcrumb */}
      <nav className="text-xs font-mono text-gray-400">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">/</span>
        <Link href="/library" className="hover:text-blue-600">Threat Library</Link>
        <span className="mx-2">/</span>
        <span className="text-gray-600">{threat.name}</span>
      </nav>

      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 sm:p-8">
        <div className="flex items-center gap-2 flex-wrap mb-3">
          <span className={`text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border ${sevStyle[threat.severity] ?? sevStyle.medium}`}>
            {threat.severity}
          </span>
          {isAgent && (
            <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border bg-purple-50 text-purple-600 border-purple-200">
              Agent Threat
            </span>
          )}
          <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border bg-blue-50 text-blue-600 border-blue-200">
            {typeLabel(threat.threat_type)}
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight leading-tight">{threat.name}</h1>
        <p className="text-xs font-mono text-gray-400 mt-3">
          First seen {fmtDate(threat.first_seen)} · Updated {fmtDate(threat.last_updated)}
          {threat.cvss_score ? ` · CVSS ${threat.cvss_score}` : ""}
        </p>
        {tags.length > 0 && (
          <div className="flex gap-1.5 mt-4 flex-wrap">
            {tags.map((tag) => (
              <span key={tag} className="text-[10px] font-mono px-2 py-0.5 bg-gray-100 rounded text-gray-500">
                {formatTag(tag)}
              </span>
            ))}
          </div>
        )}
        <p className="text-base text-gray-700 leading-relaxed mt-5">{threat.summary}</p>
      </div>

      {/* Technical analysis */}
      {threat.technical_analysis && (
        <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 sm:p-8">
          <h2 className="text-lg font-semibold">Technical Analysis</h2>
          <p className="text-sm text-gray-600 leading-relaxed mt-3 whitespace-pre-line">
            {threat.technical_analysis}
          </p>
        </section>
      )}

      {/* Affected systems */}
      {threat.affected_systems && (
        <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 sm:p-8">
          <h2 className="text-lg font-semibold">Affected Systems</h2>
          <p className="text-sm text-gray-600 leading-relaxed mt-3 whitespace-pre-line">
            {threat.affected_systems}
          </p>
        </section>
      )}

      {/* Detection indicators */}
      {iocLines.length > 0 && (
        <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 sm:p-8">
          <h2 className="text-lg font-semibold">
            {isAgent ? "Detection Signatures" : "Indicators of Compromise"}
          </h2>
          <ul className="mt-3 space-y-2">
            {iocLines.map((line, i) => (
              <li key={i} className="text-sm text-gray-600 font-mono bg-gray-50 border border-gray-100 rounded-lg px-3 py-2 break-all">
                {line}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Remediation */}
      {steps.length > 0 && (
        <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 sm:p-8">
          <h2 className="text-lg font-semibold">Remediation Steps</h2>
          <ol className="mt-4 space-y-4">
            {steps.map((step, i) => (
              <li key={i} className="flex gap-3">
                <span className="shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 text-white text-xs font-bold flex items-center justify-center mt-0.5">
                  {i + 1}
                </span>
                <div>
                  <p className="text-sm font-semibold text-gray-800">{step.title}</p>
                  <p className="text-sm text-gray-600 leading-relaxed">{step.description}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* Facts: CVEs, industries, sources */}
      {(cves.length > 0 || industries.length > 0 || sources.length > 0) && (
        <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 sm:p-8 space-y-4">
          {cves.length > 0 && (
            <div>
              <h2 className="text-xs font-mono uppercase tracking-wider text-gray-400">CVE / Advisory IDs</h2>
              <div className="flex gap-1.5 mt-2 flex-wrap">
                {cves.map((cve) => (
                  <span key={cve} className="text-xs font-mono px-2 py-1 bg-red-50 border border-red-100 rounded text-red-600">
                    {cve}
                  </span>
                ))}
              </div>
            </div>
          )}
          {industries.length > 0 && (
            <div>
              <h2 className="text-xs font-mono uppercase tracking-wider text-gray-400">Industries Most Exposed</h2>
              <div className="flex gap-1.5 mt-2 flex-wrap">
                {industries.map((ind) => (
                  <span key={ind} className="text-xs px-2 py-1 bg-gray-100 rounded text-gray-600">{ind}</span>
                ))}
              </div>
            </div>
          )}
          {sources.length > 0 && (
            <div>
              <h2 className="text-xs font-mono uppercase tracking-wider text-gray-400">Sources</h2>
              <ul className="mt-2 space-y-1">
                {sources.map((url) => (
                  <li key={url}>
                    <a href={url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline break-all">
                      {url}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {/* CTA */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-6 sm:p-8">
        <h2 className="text-lg font-semibold">Respond to this threat</h2>
        <p className="text-sm text-gray-600 mt-2 leading-relaxed">
          Pro subscribers get a full AI-generated incident-response playbook for this threat —
          detection, containment, eradication, and recovery steps — plus an unlimited AI Threat
          Advisor for questions about your environment.
        </p>
        <div className="flex items-center gap-3 mt-4 flex-wrap">
          <Link
            href={`/playbook/${threat.slug}`}
            className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90 transition-opacity"
          >
            View response playbook →
          </Link>
          <Link
            href="/library"
            className="px-5 py-2.5 rounded-lg text-sm font-semibold text-gray-700 bg-white border border-gray-200 hover:border-purple-300 transition-colors"
          >
            Browse more threats
          </Link>
        </div>
      </div>
    </div>
  );
}
