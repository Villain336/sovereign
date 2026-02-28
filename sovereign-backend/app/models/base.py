"""Base models for Sovereign platform."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --- Enums ---

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatStatus(str, Enum):
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    REMEDIATED = "remediated"
    FALSE_POSITIVE = "false_positive"


class AgentType(str, Enum):
    SENTINEL = "sentinel"
    VANGUARD = "vanguard"
    COMPLIANCE = "compliance"
    ORCHESTRATOR = "orchestrator"


class AgentStatus(str, Enum):
    RUNNING = "running"
    IDLE = "idle"
    STOPPED = "stopped"
    ERROR = "error"
    AWAITING_APPROVAL = "awaiting_approval"


class ControlStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_ASSESSED = "not_assessed"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    REMEDIATED = "remediated"
    CLOSED = "closed"


class ActionRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# --- Core Models ---

class MitreAttackTechnique(BaseModel):
    technique_id: str = Field(..., description="MITRE ATT&CK technique ID (e.g., T1566)")
    name: str = Field(..., description="Technique name")
    tactic: str = Field(..., description="Associated tactic (e.g., Initial Access)")
    description: str = Field(default="", description="Brief description")


class ThreatIndicator(BaseModel):
    indicator_type: str = Field(..., description="Type: ip, domain, hash, url, email")
    value: str = Field(..., description="Indicator value")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = Field(default="sovereign", description="Source of the indicator")


class Threat(BaseModel):
    id: str = Field(..., description="Unique threat ID")
    title: str = Field(..., description="Threat title")
    description: str = Field(default="", description="Detailed description")
    severity: Severity = Field(default=Severity.MEDIUM)
    status: ThreatStatus = Field(default=ThreatStatus.ACTIVE)
    source_ip: Optional[str] = None
    target_asset: Optional[str] = None
    mitre_techniques: List[MitreAttackTechnique] = Field(default_factory=list)
    indicators: List[ThreatIndicator] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    detected_by: str = Field(default="sentinel", description="Agent that detected this threat")
    raw_evidence: Dict[str, Any] = Field(default_factory=dict)


class Incident(BaseModel):
    id: str = Field(..., description="Unique incident ID")
    title: str = Field(..., description="Incident title")
    description: str = Field(default="")
    severity: Severity = Field(default=Severity.MEDIUM)
    status: IncidentStatus = Field(default=IncidentStatus.OPEN)
    related_threats: List[str] = Field(default_factory=list)
    affected_assets: List[str] = Field(default_factory=list)
    response_actions: List[Dict[str, Any]] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_agent: Optional[str] = None
    requires_approval: bool = False


class ResponseAction(BaseModel):
    id: str = Field(..., description="Action ID")
    action_type: str = Field(..., description="Type: isolate, block_ip, revoke_creds, quarantine, notify")
    description: str = Field(default="")
    risk_level: ActionRisk = Field(default=ActionRisk.LOW)
    target: str = Field(default="", description="Target of the action")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = Field(default=False)
    approved: Optional[bool] = None
    approved_by: Optional[str] = None
    executed: bool = False
    executed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None


class ComplianceControl(BaseModel):
    control_id: str = Field(..., description="NIST 800-171 control ID (e.g., 3.1.1)")
    family: str = Field(..., description="Control family (e.g., Access Control)")
    family_id: str = Field(..., description="Family ID (e.g., AC)")
    title: str = Field(..., description="Control title")
    description: str = Field(default="")
    status: ControlStatus = Field(default=ControlStatus.NOT_ASSESSED)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    findings: List[str] = Field(default_factory=list)
    last_assessed: Optional[datetime] = None
    assessor: str = Field(default="compliance-agent")
    cmmc_level: int = Field(default=2, description="CMMC level (1, 2, or 3)")


class AgentState(BaseModel):
    agent_id: str
    agent_type: AgentType
    status: AgentStatus = Field(default=AgentStatus.IDLE)
    name: str = Field(default="")
    description: str = Field(default="")
    started_at: Optional[datetime] = None
    last_action_at: Optional[datetime] = None
    actions_taken: int = 0
    current_task: Optional[str] = None
    memory: List[Dict[str, Any]] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)


class AuditEntry(BaseModel):
    id: str = Field(..., description="Unique audit entry ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: str = Field(..., description="Who performed the action (agent ID or user)")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(default="", description="Type of resource affected")
    resource_id: str = Field(default="", description="ID of resource affected")
    details: Dict[str, Any] = Field(default_factory=dict)
    hash: str = Field(default="", description="SHA-256 hash of this entry")
    previous_hash: str = Field(default="", description="Hash of previous entry (chain)")
    integrity_verified: bool = True


class DashboardSummary(BaseModel):
    total_threats: int = 0
    active_threats: int = 0
    critical_threats: int = 0
    total_incidents: int = 0
    open_incidents: int = 0
    compliance_score: float = 0.0
    controls_compliant: int = 0
    controls_total: int = 110
    agents_running: int = 0
    agents_total: int = 0
    pending_approvals: int = 0
    last_scan_at: Optional[datetime] = None
    audit_entries_count: int = 0
    threat_trend: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_by_family: List[Dict[str, Any]] = Field(default_factory=list)
