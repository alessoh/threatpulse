import type { Metadata } from "next";
import Script from "next/script";
import Link from "next/link";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import Nav from "@/components/ui/Nav";

export const metadata: Metadata = {
  // Base for resolving canonical URLs and Open Graph images site-wide.
  metadataBase: new URL("https://threatpulse.dev"),
  title: "ThreatPulse — Threat intelligence for the age of AI agents",
  description:
    "Agent-first threat intelligence: prompt injection, MCP tool poisoning, agent worms, and framework CVEs explained in plain English — with conventional vulnerabilities on the watchlist.",
  openGraph: {
    type: "website",
    siteName: "ThreatPulse",
    title: "ThreatPulse — Threat intelligence for the age of AI agents",
    description:
      "Agent-first threat intelligence: prompt injection, MCP tool poisoning, agent worms, and framework CVEs explained in plain English.",
    url: "/",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "ThreatPulse — Threat intelligence for the age of AI agents",
    description:
      "Agent-first threat intelligence: prompt injection, MCP tool poisoning, agent worms, and framework CVEs explained in plain English.",
  },
  // Renders <meta name="google-site-verification" content="..."> for Google
  // Search Console site ownership verification.
  verification: {
    google: "N8fXikxXAf9Ai2mt9t-sfHHlTubRfn8Yozdou0eh-To",
  },
};

// Organization + WebSite structured data (with a sitelinks-search action
// pointing at the library search), rendered once on every page.
const JSON_LD = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://threatpulse.dev/#organization",
      name: "ThreatPulse",
      url: "https://threatpulse.dev",
      description:
        "Agent-first cyber threat intelligence: threats to and between AI agents, explained in plain English.",
    },
    {
      "@type": "WebSite",
      "@id": "https://threatpulse.dev/#website",
      name: "ThreatPulse",
      url: "https://threatpulse.dev",
      publisher: { "@id": "https://threatpulse.dev/#organization" },
      potentialAction: {
        "@type": "SearchAction",
        target: {
          "@type": "EntryPoint",
          urlTemplate: "https://threatpulse.dev/library?search={search_term_string}",
        },
        "query-input": "required name=search_term_string",
      },
    },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#f8f9fc] flex flex-col">
        {/* Ahrefs Web Analytics */}
        <Script
          src="https://analytics.ahrefs.com/analytics.js"
          data-key="uoTyKDoOKhXcxU8Wo04u7A"
          strategy="afterInteractive"
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(JSON_LD) }}
        />
        <AuthProvider>
          <Nav />
          <main className="max-w-7xl mx-auto w-full px-4 py-6 flex-1">{children}</main>
          <footer className="border-t border-gray-200 bg-white mt-6">
            <div className="max-w-7xl mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between gap-2">
              <p className="text-xs text-gray-400">
                © 2026 ThreatPulse · Threat intelligence for the age of AI agents.
              </p>
              <Link href="/terms" className="text-xs text-gray-500 hover:text-blue-600">
                Terms of Service
              </Link>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
