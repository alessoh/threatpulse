// Human-readable labels for the agent-threat taxonomy.
// ASI ids follow the OWASP Agentic Top 10; the names mirror the taxonomy
// comments in backend/app/services/ai_service.py.

export const ASI_LABELS: Record<string, string> = {
  ASI01: "Goal Hijacking",
  ASI02: "Tool Misuse",
  ASI03: "Identity Spoofing",
  ASI04: "Agentic Supply Chain",
  ASI05: "Unsafe Code Execution",
  ASI06: "Memory Poisoning",
  ASI07: "Inter-Agent Comms",
  ASI08: "Cascading Failures",
  ASI09: "Human Trust Exploitation",
  ASI10: "Rogue Agents",
};

export const TYPE_LABELS: Record<string, string> = {
  // agent taxonomy
  "goal-hijack": "Goal Hijack",
  "prompt-injection": "Prompt Injection",
  "tool-poisoning": "Tool Poisoning",
  "tool-misuse": "Tool Misuse",
  "identity-spoofing": "Identity Spoofing",
  "privilege-abuse": "Privilege Abuse",
  "code-execution": "Code Execution",
  "memory-poisoning": "Memory Poisoning",
  "inter-agent-comms": "Inter-Agent Comms",
  "cascading-failure": "Cascading Failure",
  "human-trust-exploitation": "Human Trust Exploitation",
  "rogue-agent": "Rogue Agent",
  "protocol-vulnerability": "Protocol Vulnerability",
  "framework-vulnerability": "Framework Vulnerability",
  "resource-exhaustion": "Resource Exhaustion",
  "data-exfiltration": "Data Exfiltration",
  "agent-worm": "Agent Worm",
  // conventional taxonomy
  ransomware: "Ransomware",
  apt: "APT",
  "zero-day": "Zero-Day",
  "supply-chain": "Supply Chain",
  phishing: "Phishing",
  malware: "Malware",
  other: "Other",
};

export function typeLabel(threatType: string): string {
  return TYPE_LABELS[threatType] || threatType;
}

const titleCase = (s: string) =>
  s.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

/** Turn a raw stored tag ("ASI04", "surface:tool-layer",
 *  "propagation:self-propagating") into something a human can read. */
export function formatTag(rawTag: string): string {
  const tag = rawTag.trim();
  const asi = tag.toUpperCase();
  if (ASI_LABELS[asi]) return `${asi} · ${ASI_LABELS[asi]}`;
  if (tag.toLowerCase().startsWith("surface:"))
    return `Surface: ${titleCase(tag.slice(8))}`;
  if (tag.toLowerCase().startsWith("propagation:"))
    return `Propagation: ${titleCase(tag.slice(12))}`;
  return tag;
}
