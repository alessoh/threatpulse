import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import Nav from "@/components/ui/Nav";

export const metadata: Metadata = {
  title: "ThreatPulse — Threat intelligence for the age of AI agents",
  description:
    "Agent-first threat intelligence: prompt injection, MCP tool poisoning, agent worms, and framework CVEs explained in plain English — with conventional vulnerabilities on the watchlist.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#f8f9fc]">
        <AuthProvider>
          <Nav />
          <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
