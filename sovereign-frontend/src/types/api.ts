export interface MitreAttackTechnique {
  technique_id: string;
  name: string;
  tactic: string;
  description: string;
}

export interface ThreatIndicator {
  indicator_type: string;
  value: string;
  confidence: number;
  source: string;
}

export interface Threat {
  id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  status: "active" | "investigating" | "contained" | "remediated" | "false_positive";
  source_ip: string | null;
  target_asset: string | null;
  mitre_techniques: MitreAttackTechnique[];
  indicators: ThreatIndicator[];
  confidence: number;
  detected_at: string;
  updated_at: string;
  detected_by: string;
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  status: "open" | "investigating" | "contained" | "remediated" | "closed";
  related_threats: string[];
  affected_assets: string[];
  response_actions: Array<{ action: string; status: string; timestamp: string }>;
  timeline: Array<{ event: string; timestamp: string }>;
  created_at: string;
  updated_at: string;
  assigned_agent: string | null;
  requires_approval: boolean;
}

export interface ComplianceControl {
  control_id: string;
  family: string;
  family_id: string;
  title: string;
  description: string;
  status: "compliant" | "non_compliant" | "partially_compliant" | "not_assessed";
  evidence: Array<Record<string, unknown>>;
  findings: string[];
  last_assessed: string | null;
  assessor: string;
  cmmc_level: number;
}

export interface AgentState {
  agent_id: string;
  agent_type: "sentinel" | "vanguard" | "compliance" | "orchestrator";
  status: "running" | "idle" | "stopped" | "error" | "awaiting_approval";
  name: string;
  description: string;
  started_at: string | null;
  last_action_at: string | null;
  actions_taken: number;
  current_task: string | null;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, unknown>;
  hash: string;
  previous_hash: string;
  integrity_verified: boolean;
}

export interface ResponseAction {
  id: string;
  action_type: string;
  description: string;
  risk_level: "low" | "medium" | "high" | "critical";
  target: string;
  parameters: Record<string, unknown>;
  requires_approval: boolean;
  approved: boolean | null;
  executed: boolean;
}

export interface DashboardSummary {
  total_threats: number;
  active_threats: number;
  critical_threats: number;
  total_incidents: number;
  open_incidents: number;
  compliance_score: number;
  controls_compliant: number;
  controls_total: number;
  agents_running: number;
  agents_total: number;
  pending_approvals: number;
  last_scan_at: string | null;
  audit_entries_count: number;
  threat_trend: Array<{ hour: string; threats: number }>;
  compliance_by_family: Array<{
    family: string;
    family_id: string;
    total: number;
    compliant: number;
    score: number;
  }>;
}

export interface ComplianceFamilyStatus {
  family_id: string;
  family: string;
  total: number;
  compliant: number;
  partially_compliant: number;
  non_compliant: number;
  not_assessed: number;
  score: number;
}

export interface ComplianceStatus {
  overall_score: number;
  total_controls: number;
  compliant: number;
  partially_compliant: number;
  non_compliant: number;
  not_assessed: number;
  cmmc_level: number;
  framework: string;
  families: ComplianceFamilyStatus[];
}
