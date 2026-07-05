import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Terms of Service — ThreatPulse",
  description:
    "ThreatPulse Terms of Service: service description, disclaimers, limitation of liability, subscriptions, data and privacy, and governing law.",
  alternates: { canonical: "/terms" },
};

const EFFECTIVE_DATE = "July 7, 2026";

// Each section is a heading plus one or more paragraphs, rendered in order.
// Paragraphs are ReactNode so a section (e.g. Contact) can embed a link.
const SECTIONS: { title: string; body: ReactNode[] }[] = [
  {
    title: "1. Service Description",
    body: [
      "ThreatPulse is an informational cyber threat intelligence platform that aggregates and synthesizes publicly available security data. The platform provides threat assessments, remediation guidance, and AI-powered advisory features for educational and informational purposes.",
    ],
  },
  {
    title: "2. No Professional Security Advice",
    body: [
      "The information provided through ThreatPulse, including threat profiles, remediation playbooks, severity assessments, and AI Threat Advisor responses, is provided for general informational purposes only. It does not constitute professional cybersecurity consulting, legal advice, compliance guidance, or a substitute for the services of a qualified information security professional.",
      "ThreatPulse does not perform security assessments of your specific environment. The threat data, remediation steps, and recommendations presented on this platform are generalized and may not be appropriate for your particular systems, network architecture, regulatory requirements, or risk profile. You should always consult with a qualified cybersecurity professional before implementing any security changes to your environment.",
    ],
  },
  {
    title: "3. No Guarantee of Completeness or Accuracy",
    body: [
      "ThreatPulse aggregates information from publicly available sources including government advisories, vulnerability databases, vendor security bulletins, and open-source threat feeds. While we make reasonable efforts to present accurate and current information, we do not warrant that any information on this platform is complete, accurate, reliable, current, or error-free.",
      "Cyber threats evolve rapidly. Threat profiles, severity assessments, indicators of compromise, and remediation guidance may become outdated between updates. New vulnerabilities, attack variants, and threat actor tactics may emerge at any time that are not yet reflected on this platform. The absence of a threat from our database does not mean the threat does not exist.",
    ],
  },
  {
    title: "4. AI-Generated Content",
    body: [
      "Portions of the content on ThreatPulse, including threat summaries, remediation guidance, and AI Threat Advisor responses, are generated or synthesized using artificial intelligence models. AI-generated content may contain errors, omissions, or inaccuracies. AI-generated content should not be relied upon as the sole basis for security decisions. Users should independently verify any AI-generated information before acting on it, particularly when implementing changes to production systems, security configurations, or incident response procedures.",
    ],
  },
  {
    title: "5. Limitation of Liability",
    body: [
      "To the fullest extent permitted by applicable law, ThreatPulse, its owners, operators, employees, and affiliates shall not be liable for any direct, indirect, incidental, consequential, special, or exemplary damages arising from or related to your use of this platform, including but not limited to damages resulting from security incidents, data breaches, system outages, business interruption, loss of data, loss of revenue, or any other losses, whether or not ThreatPulse was advised of the possibility of such damages.",
      "This limitation applies to all information, content, recommendations, and guidance provided through the platform, including content accessed through free or paid subscription tiers, AI Threat Advisor responses, email notifications, and API data feeds.",
    ],
  },
  {
    title: "6. No Warranty",
    body: [
      'ThreatPulse is provided on an "as is" and "as available" basis without warranties of any kind, either express or implied, including but not limited to implied warranties of merchantability, fitness for a particular purpose, non-infringement, or course of performance.',
      "We do not warrant that the platform will be uninterrupted, secure, or free from errors. We do not warrant that the results obtained from the use of the platform will be accurate or reliable. We do not warrant that any defects in the platform will be corrected.",
    ],
  },
  {
    title: "7. Indemnification",
    body: [
      "You agree to indemnify, defend, and hold harmless ThreatPulse and its owners, operators, employees, and affiliates from and against any claims, liabilities, damages, losses, costs, and expenses (including reasonable legal fees) arising from or related to your use of the platform, your violation of these terms, or your violation of any rights of any third party.",
    ],
  },
  {
    title: "8. Subscriptions and Payments",
    body: [
      "Paid subscriptions are billed on a recurring monthly basis through our payment processor. You may cancel your subscription at any time. Upon cancellation, your access to paid features will continue until the end of your current billing period. Refunds are not provided for partial billing periods.",
      "Prices are subject to change. We will provide at least 30 days notice before any price increase takes effect for existing subscribers.",
    ],
  },
  {
    title: "9. Data and Privacy",
    body: [
      "ThreatPulse collects the minimum information necessary to provide the service, including your email address, subscription tier, and any profile preferences you voluntarily provide (such as industry and technology stack selections used to filter threat alerts).",
      "We do not sell your personal information to third parties. We do not share your information with third parties except as necessary to process payments (through our payment processor) and send email notifications (through our email service provider).",
      "If you use the AI Threat Advisor feature with your own API key, your API key is processed entirely within your browser and is not transmitted to or stored by ThreatPulse servers.",
      "The practices described in this Data and Privacy section reflect how ThreatPulse handles your information.",
    ],
  },
  {
    title: "10. Intellectual Property",
    body: [
      "All content on ThreatPulse, including threat profiles, remediation playbooks, visualizations, and platform design, is the property of ThreatPulse or its licensors. Threat data sourced from government agencies (CISA, NVD, MITRE) is public domain or used in accordance with applicable terms.",
      "Paid subscribers may use ThreatPulse content internally within their organization. Redistribution, resale, or republication of ThreatPulse content without written permission is prohibited.",
    ],
  },
  {
    title: "11. Governing Law",
    body: [
      "These terms shall be governed by and construed in accordance with the laws of the State of California, without regard to its conflict of law provisions. Any disputes arising from these terms or your use of the platform shall be resolved in the state and federal courts located in California.",
    ],
  },
  {
    title: "12. Changes to Terms",
    body: [
      "We reserve the right to modify these terms at any time. Changes take effect when posted on this page. Your continued use of the platform after changes are posted constitutes acceptance of the modified terms.",
    ],
  },
  {
    title: "13. Contact",
    body: [
      <>
        For questions about these terms, contact us at{" "}
        <a
          href="mailto:hpalesso91@gmail.com"
          className="text-blue-600 hover:underline"
        >
          hpalesso91@gmail.com
        </a>
        .
      </>,
    ],
  },
];

export default function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto py-8">
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 sm:p-10">
        <h1 className="text-3xl font-bold tracking-tight">Terms of Service</h1>
        <p className="text-sm text-gray-500 mt-2">{EFFECTIVE_DATE}</p>

        <div className="mt-8 space-y-8">
          {SECTIONS.map((section) => (
            <section key={section.title}>
              <h2 className="text-lg font-semibold text-gray-900">{section.title}</h2>
              <div className="mt-2 space-y-3">
                {section.body.map((paragraph, i) => (
                  <p key={i} className="text-sm text-gray-600 leading-relaxed">
                    {paragraph}
                  </p>
                ))}
              </div>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
