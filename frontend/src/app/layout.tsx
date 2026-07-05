import type { Metadata } from "next";
import Script from "next/script";
import Link from "next/link";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import Nav from "@/components/ui/Nav";

export const metadata: Metadata = {
  title: "ThreatPulse — Threat intelligence for the age of AI agents",
  description:
    "Agent-first threat intelligence: prompt injection, MCP tool poisoning, agent worms, and framework CVEs explained in plain English — with conventional vulnerabilities on the watchlist.",
  // Renders <meta name="google-site-verification" content="..."> for Google
  // Search Console site ownership verification.
  verification: {
    google: "N8fXikxXAf9Ai2mt9t-sfHHlTubRfn8Yozdou0eh-To",
  },
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
