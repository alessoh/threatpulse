export interface User {
  id: number;
  email: string;
  full_name: string;
  company: string;
  tier: "free" | "pro" | "enterprise";
  industry: string;
  tech_stack: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Threat {
  id: number;
  name: string;
  slug: string;
  severity: "critical" | "high" | "medium" | "low";
  threat_type: string;
  tags: string;
  summary: string;
  cvss_score: number | null;
  is_active: boolean;
  first_seen: string;
  last_updated: string;
}

export interface ThreatDetail extends Threat {
  technical_analysis: string;
  affected_systems: string;
  iocs: string;
  remediation_steps: string;
  source_urls: string;
  cve_ids: string;
  industries_affected: string;
}

export interface ThreatListResponse {
  threats: Threat[];
  total: number;
  page: number;
  per_page: number;
}

export interface DashboardStats {
  critical_count: number;
  high_count: number;
  active_campaigns: number;
  sources_monitored: number;
  critical_delta: number;
  high_delta: number;
}

export interface DailyInsight {
  insight: string | null;
  generated_at: string | null;
  model: string | null;
}

export interface Playbook {
  id: number;
  threat_id: number;
  title: string;
  executive_summary: string;
  technical_details: string;
  steps_json: string;
  yara_rules: string;
  config_templates: string;
  tier_required: string;
}
