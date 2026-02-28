"""In-memory state management for Sovereign MVP.

Provides thread-safe access to all platform state including threats,
incidents, compliance controls, agents, and audit trail.
"""

import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

from app.compliance.nist_controls import (
    CONTROL_FAMILIES,
    NIST_800_171_CONTROLS,
    MITRE_ATTACK_TECHNIQUES,
)
from app.core.security import (
    compute_chain_hash,
    generate_event_id,
)
from app.models.base import (
    ActionRisk,
    AgentState,
    AgentStatus,
    AgentType,
    AuditEntry,
    ComplianceControl,
    ControlStatus,
    DashboardSummary,
    Incident,
    IncidentStatus,
    MitreAttackTechnique,
    ResponseAction,
    Severity,
    Threat,
    ThreatIndicator,
    ThreatStatus,
)


class PlatformState:
    """Thread-safe in-memory state store for the Sovereign platform."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.threats: Dict[str, Threat] = {}
        self.incidents: Dict[str, Incident] = {}
        self.controls: Dict[str, ComplianceControl] = {}
        self.agents: Dict[str, AgentState] = {}
        self.audit_trail: List[AuditEntry] = []
        self.pending_actions: Dict[str, ResponseAction] = {}
        self._last_audit_hash: Optional[str] = None

        # Initialize on creation
        self._init_controls()
        self._init_agents()
        self._seed_realistic_data()

    def _init_controls(self) -> None:
        """Initialize all 110 NIST 800-171 controls."""
        for ctrl in NIST_800_171_CONTROLS:
            family_name = CONTROL_FAMILIES.get(ctrl["family"], ctrl["family"])
            self.controls[ctrl["id"]] = ComplianceControl(
                control_id=ctrl["id"],
                family=family_name,
                family_id=ctrl["family"],
                title=ctrl["title"],
                description=ctrl.get("description", ""),
                status=ControlStatus.NOT_ASSESSED,
                cmmc_level=2,
            )

    def _init_agents(self) -> None:
        """Initialize the default agent pool."""
        default_agents = [
            AgentState(
                agent_id="sentinel-alpha",
                agent_type=AgentType.SENTINEL,
                name="Sentinel Alpha",
                description="Primary network threat detection agent. Monitors network flows, DNS queries, and connection patterns for indicators of compromise.",
                status=AgentStatus.RUNNING,
                started_at=datetime.utcnow() - timedelta(hours=6),
                last_action_at=datetime.utcnow() - timedelta(minutes=2),
                actions_taken=847,
                current_task="Monitoring network traffic patterns",
            ),
            AgentState(
                agent_id="sentinel-bravo",
                agent_type=AgentType.SENTINEL,
                name="Sentinel Bravo",
                description="Endpoint telemetry analysis agent. Processes endpoint detection data, file integrity changes, and process execution logs.",
                status=AgentStatus.RUNNING,
                started_at=datetime.utcnow() - timedelta(hours=6),
                last_action_at=datetime.utcnow() - timedelta(minutes=5),
                actions_taken=623,
                current_task="Analyzing endpoint process trees",
            ),
            AgentState(
                agent_id="sentinel-charlie",
                agent_type=AgentType.SENTINEL,
                name="Sentinel Charlie",
                description="Identity and access monitoring agent. Detects anomalous authentication patterns, privilege escalation attempts, and credential abuse.",
                status=AgentStatus.RUNNING,
                started_at=datetime.utcnow() - timedelta(hours=6),
                last_action_at=datetime.utcnow() - timedelta(minutes=1),
                actions_taken=412,
                current_task="Correlating authentication events",
            ),
            AgentState(
                agent_id="vanguard-prime",
                agent_type=AgentType.VANGUARD,
                name="Vanguard Prime",
                description="Primary incident response agent. Executes containment playbooks, isolates compromised assets, and orchestrates remediation workflows.",
                status=AgentStatus.RUNNING,
                started_at=datetime.utcnow() - timedelta(hours=6),
                last_action_at=datetime.utcnow() - timedelta(minutes=15),
                actions_taken=56,
                current_task="Standing by for incident response",
            ),
            AgentState(
                agent_id="compliance-one",
                agent_type=AgentType.COMPLIANCE,
                name="Compliance Monitor",
                description="Continuous compliance assessment agent. Monitors all 110 NIST 800-171 controls, collects evidence, and generates POA&M documents.",
                status=AgentStatus.RUNNING,
                started_at=datetime.utcnow() - timedelta(hours=6),
                last_action_at=datetime.utcnow() - timedelta(minutes=30),
                actions_taken=110,
                current_task="Assessing Access Control family",
            ),
            AgentState(
                agent_id="orchestrator-main",
                agent_type=AgentType.ORCHESTRATOR,
                name="Orchestrator",
                description="Central coordination agent. Plans multi-agent workflows, manages agent communication, and enforces human-in-the-loop policies.",
                status=AgentStatus.RUNNING,
                started_at=datetime.utcnow() - timedelta(hours=6),
                last_action_at=datetime.utcnow() - timedelta(seconds=30),
                actions_taken=2341,
                current_task="Coordinating agent activities",
            ),
        ]
        for agent in default_agents:
            self.agents[agent.agent_id] = agent

    def _seed_realistic_data(self) -> None:
        """Seed realistic threat, incident, and compliance data for demo."""
        now = datetime.utcnow()

        # Seed threats with realistic defense-sector scenarios
        threats_data = [
            {
                "id": generate_event_id(),
                "title": "APT-41 C2 Beacon Detected on Engineering Workstation",
                "description": "Network analysis detected periodic HTTPS beaconing to a known APT-41 command and control domain (update.microsoftcloud-cdn[.]com). The beacon interval of 60 seconds with 10% jitter matches known APT-41 Cobalt Strike malleable C2 profiles. Source workstation belongs to the CUI-processing engineering subnet.",
                "severity": Severity.CRITICAL,
                "status": ThreatStatus.INVESTIGATING,
                "source_ip": "10.10.50.22",
                "target_asset": "ENG-WS-0142 (Engineering Workstation)",
                "mitre_techniques": [
                    MitreAttackTechnique(technique_id="T1071", name="Application Layer Protocol", tactic="Command and Control", description="C2 over HTTPS"),
                    MitreAttackTechnique(technique_id="T1566.001", name="Spearphishing Attachment", tactic="Initial Access", description="Initial vector via weaponized PDF"),
                ],
                "indicators": [
                    ThreatIndicator(indicator_type="domain", value="update.microsoftcloud-cdn.com", confidence=0.95, source="sovereign-sentinel"),
                    ThreatIndicator(indicator_type="ip", value="185.141.63.120", confidence=0.92, source="sovereign-sentinel"),
                    ThreatIndicator(indicator_type="hash", value="a3f5b8c2d1e4f6789012345678abcdef01234567", confidence=0.88, source="sovereign-sentinel"),
                ],
                "confidence": 0.94,
                "detected_at": now - timedelta(minutes=45),
                "detected_by": "sentinel-alpha",
            },
            {
                "id": generate_event_id(),
                "title": "Credential Stuffing Attack on VPN Gateway",
                "description": "Detected 2,847 failed authentication attempts against the corporate VPN gateway from 12 unique source IPs over a 30-minute window. The attack pattern matches credential stuffing using leaked credential databases. Three valid accounts were successfully accessed.",
                "severity": Severity.HIGH,
                "status": ThreatStatus.CONTAINED,
                "source_ip": "Multiple (12 IPs)",
                "target_asset": "VPN-GW-01 (Corporate VPN Gateway)",
                "mitre_techniques": [
                    MitreAttackTechnique(technique_id="T1110", name="Brute Force", tactic="Credential Access", description="Credential stuffing attack"),
                    MitreAttackTechnique(technique_id="T1078", name="Valid Accounts", tactic="Defense Evasion", description="Compromised valid credentials"),
                ],
                "indicators": [
                    ThreatIndicator(indicator_type="ip", value="91.234.56.78", confidence=0.98, source="sovereign-sentinel"),
                    ThreatIndicator(indicator_type="ip", value="103.45.67.89", confidence=0.97, source="sovereign-sentinel"),
                ],
                "confidence": 0.97,
                "detected_at": now - timedelta(hours=2),
                "detected_by": "sentinel-charlie",
            },
            {
                "id": generate_event_id(),
                "title": "Suspicious PowerShell Execution on Domain Controller",
                "description": "Sentinel detected encoded PowerShell commands executing on DC-01 that match known credential dumping techniques. The commands attempt to access LSASS memory and export Active Directory credentials. This could indicate lateral movement following initial compromise.",
                "severity": Severity.CRITICAL,
                "status": ThreatStatus.ACTIVE,
                "source_ip": "10.10.10.5",
                "target_asset": "DC-01 (Primary Domain Controller)",
                "mitre_techniques": [
                    MitreAttackTechnique(technique_id="T1059.001", name="PowerShell", tactic="Execution", description="Encoded PowerShell execution"),
                    MitreAttackTechnique(technique_id="T1003", name="OS Credential Dumping", tactic="Credential Access", description="LSASS memory access attempt"),
                ],
                "indicators": [
                    ThreatIndicator(indicator_type="hash", value="b4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3", confidence=0.91, source="sovereign-sentinel"),
                ],
                "confidence": 0.89,
                "detected_at": now - timedelta(minutes=12),
                "detected_by": "sentinel-bravo",
            },
            {
                "id": generate_event_id(),
                "title": "Anomalous Data Exfiltration via DNS Tunneling",
                "description": "Detected anomalous DNS query patterns from file server FS-CUI-03 that match DNS tunneling techniques. Over 15,000 unique DNS TXT queries were sent to a suspicious domain in the past hour, with encoded payloads averaging 180 bytes per query. The file server hosts CUI export-controlled technical data.",
                "severity": Severity.HIGH,
                "status": ThreatStatus.ACTIVE,
                "source_ip": "10.10.30.15",
                "target_asset": "FS-CUI-03 (CUI File Server)",
                "mitre_techniques": [
                    MitreAttackTechnique(technique_id="T1048", name="Exfiltration Over Alternative Protocol", tactic="Exfiltration", description="DNS tunneling for data exfiltration"),
                    MitreAttackTechnique(technique_id="T1005", name="Data from Local System", tactic="Collection", description="Collection of local files"),
                ],
                "indicators": [
                    ThreatIndicator(indicator_type="domain", value="ns1.data-analytics-corp.xyz", confidence=0.87, source="sovereign-sentinel"),
                ],
                "confidence": 0.86,
                "detected_at": now - timedelta(minutes=28),
                "detected_by": "sentinel-alpha",
            },
            {
                "id": generate_event_id(),
                "title": "Supply Chain Risk: Compromised npm Package in Build Pipeline",
                "description": "Automated supply chain monitoring detected that npm package 'lodash-utils-ext@2.1.4', used in the internal web application build pipeline, was flagged by multiple threat intelligence feeds as containing a backdoor. The package was added to the project 48 hours ago by a developer.",
                "severity": Severity.MEDIUM,
                "status": ThreatStatus.INVESTIGATING,
                "source_ip": "N/A",
                "target_asset": "CI/CD Pipeline (Jenkins-01)",
                "mitre_techniques": [
                    MitreAttackTechnique(technique_id="T1195", name="Supply Chain Compromise", tactic="Initial Access", description="Compromised third-party software"),
                ],
                "indicators": [
                    ThreatIndicator(indicator_type="hash", value="e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4", confidence=0.82, source="sovereign-sentinel"),
                ],
                "confidence": 0.82,
                "detected_at": now - timedelta(hours=1, minutes=15),
                "detected_by": "sentinel-bravo",
            },
            {
                "id": generate_event_id(),
                "title": "Unauthorized Wireless Access Point Detected",
                "description": "Network monitoring detected a rogue wireless access point broadcasting SSID 'CorpWiFi-Guest' in Building C, Floor 3. The AP is not registered in the authorized device inventory and may be used for man-in-the-middle attacks or unauthorized network access.",
                "severity": Severity.MEDIUM,
                "status": ThreatStatus.ACTIVE,
                "source_ip": "N/A",
                "target_asset": "Building C, Floor 3 Network Segment",
                "mitre_techniques": [
                    MitreAttackTechnique(technique_id="T1199", name="Trusted Relationship", tactic="Initial Access", description="Rogue access point exploitation"),
                ],
                "indicators": [
                    ThreatIndicator(indicator_type="ip", value="10.10.99.254", confidence=0.78, source="sovereign-sentinel"),
                ],
                "confidence": 0.78,
                "detected_at": now - timedelta(hours=3),
                "detected_by": "sentinel-alpha",
            },
        ]

        for td in threats_data:
            self.threats[td["id"]] = Threat(**td)

        # Seed incidents
        threat_ids = list(self.threats.keys())
        incidents_data = [
            Incident(
                id=generate_event_id(),
                title="APT-41 Intrusion - Engineering Subnet Compromise",
                description="Multi-stage intrusion linked to APT-41 threat actor. Initial access via spearphishing, followed by C2 establishment on engineering workstation. Potential access to CUI-designated technical data. Vanguard agent has initiated network isolation of affected subnet.",
                severity=Severity.CRITICAL,
                status=IncidentStatus.INVESTIGATING,
                related_threats=[threat_ids[0], threat_ids[2]],
                affected_assets=["ENG-WS-0142", "DC-01", "10.10.50.0/24 subnet"],
                response_actions=[
                    {"action": "Network segment isolation", "status": "completed", "timestamp": (now - timedelta(minutes=40)).isoformat()},
                    {"action": "Endpoint forensic capture initiated", "status": "in_progress", "timestamp": (now - timedelta(minutes=35)).isoformat()},
                    {"action": "Credential reset for affected accounts", "status": "pending_approval", "timestamp": (now - timedelta(minutes=30)).isoformat()},
                ],
                timeline=[
                    {"event": "C2 beacon detected by Sentinel Alpha", "timestamp": (now - timedelta(minutes=45)).isoformat()},
                    {"event": "Orchestrator escalated to Vanguard Prime", "timestamp": (now - timedelta(minutes=44)).isoformat()},
                    {"event": "Vanguard Prime initiated subnet isolation", "timestamp": (now - timedelta(minutes=40)).isoformat()},
                    {"event": "Correlated with PowerShell activity on DC-01", "timestamp": (now - timedelta(minutes=12)).isoformat()},
                    {"event": "Credential reset queued - awaiting human approval", "timestamp": (now - timedelta(minutes=10)).isoformat()},
                ],
                created_at=now - timedelta(minutes=44),
                assigned_agent="vanguard-prime",
                requires_approval=True,
            ),
            Incident(
                id=generate_event_id(),
                title="Credential Stuffing Attack - VPN Gateway",
                description="Large-scale credential stuffing attack against corporate VPN gateway. Three valid accounts compromised. Vanguard agent has locked affected accounts, blocked source IPs, and initiated forced password resets.",
                severity=Severity.HIGH,
                status=IncidentStatus.CONTAINED,
                related_threats=[threat_ids[1]],
                affected_assets=["VPN-GW-01", "3 user accounts"],
                response_actions=[
                    {"action": "Blocked 12 source IPs at firewall", "status": "completed", "timestamp": (now - timedelta(hours=1, minutes=50)).isoformat()},
                    {"action": "Locked 3 compromised accounts", "status": "completed", "timestamp": (now - timedelta(hours=1, minutes=48)).isoformat()},
                    {"action": "Forced password reset initiated", "status": "completed", "timestamp": (now - timedelta(hours=1, minutes=45)).isoformat()},
                    {"action": "VPN session audit completed", "status": "completed", "timestamp": (now - timedelta(hours=1, minutes=30)).isoformat()},
                ],
                timeline=[
                    {"event": "Brute force pattern detected by Sentinel Charlie", "timestamp": (now - timedelta(hours=2)).isoformat()},
                    {"event": "Vanguard Prime auto-blocked source IPs (low-risk action)", "timestamp": (now - timedelta(hours=1, minutes=50)).isoformat()},
                    {"event": "Three successful logins identified", "timestamp": (now - timedelta(hours=1, minutes=49)).isoformat()},
                    {"event": "Accounts locked and password resets initiated", "timestamp": (now - timedelta(hours=1, minutes=48)).isoformat()},
                    {"event": "Incident contained - no lateral movement detected", "timestamp": (now - timedelta(hours=1, minutes=30)).isoformat()},
                ],
                created_at=now - timedelta(hours=2),
                assigned_agent="vanguard-prime",
                requires_approval=False,
            ),
            Incident(
                id=generate_event_id(),
                title="CUI Data Exfiltration Attempt via DNS Tunneling",
                description="Active data exfiltration attempt detected from CUI file server via DNS tunneling. The file server contains ITAR-controlled technical data. Immediate isolation recommended. Awaiting human approval for file server shutdown.",
                severity=Severity.CRITICAL,
                status=IncidentStatus.OPEN,
                related_threats=[threat_ids[3]],
                affected_assets=["FS-CUI-03"],
                response_actions=[
                    {"action": "DNS query blocking for suspicious domain", "status": "completed", "timestamp": (now - timedelta(minutes=25)).isoformat()},
                    {"action": "File server network isolation", "status": "pending_approval", "timestamp": (now - timedelta(minutes=24)).isoformat()},
                ],
                timeline=[
                    {"event": "DNS tunneling pattern detected by Sentinel Alpha", "timestamp": (now - timedelta(minutes=28)).isoformat()},
                    {"event": "Suspicious domain blocked at DNS resolver", "timestamp": (now - timedelta(minutes=25)).isoformat()},
                    {"event": "File server isolation pending human approval (CUI asset)", "timestamp": (now - timedelta(minutes=24)).isoformat()},
                ],
                created_at=now - timedelta(minutes=28),
                assigned_agent="vanguard-prime",
                requires_approval=True,
            ),
        ]

        for inc in incidents_data:
            self.incidents[inc.id] = inc

        # Seed compliance assessment with realistic statuses
        # Simulate a partial assessment - some compliant, some non-compliant, some not assessed
        assessed_controls = {}
        compliant_ratio = 0.62
        partial_ratio = 0.15
        non_compliant_ratio = 0.10
        # 13% remain not_assessed

        random.seed(42)  # Deterministic for consistent demo
        for control_id, control in self.controls.items():
            roll = random.random()
            if roll < compliant_ratio:
                control.status = ControlStatus.COMPLIANT
                control.last_assessed = now - timedelta(hours=random.randint(1, 48))
                control.evidence = [{"type": "automated_scan", "timestamp": control.last_assessed.isoformat(), "result": "pass", "agent": "compliance-one"}]
            elif roll < compliant_ratio + partial_ratio:
                control.status = ControlStatus.PARTIALLY_COMPLIANT
                control.last_assessed = now - timedelta(hours=random.randint(1, 48))
                control.findings = [f"Partial implementation detected for {control.family_id}.{control.control_id}"]
                control.evidence = [{"type": "automated_scan", "timestamp": control.last_assessed.isoformat(), "result": "partial", "agent": "compliance-one"}]
            elif roll < compliant_ratio + partial_ratio + non_compliant_ratio:
                control.status = ControlStatus.NON_COMPLIANT
                control.last_assessed = now - timedelta(hours=random.randint(1, 48))
                control.findings = [f"Control {control.control_id} not implemented or ineffective"]
                control.evidence = [{"type": "automated_scan", "timestamp": control.last_assessed.isoformat(), "result": "fail", "agent": "compliance-one"}]

        # Seed pending actions requiring human approval
        self.pending_actions["action-001"] = ResponseAction(
            id="action-001",
            action_type="isolate",
            description="Isolate CUI file server FS-CUI-03 from network to stop active DNS tunneling exfiltration. This will interrupt ongoing file access for 23 users.",
            risk_level=ActionRisk.HIGH,
            target="FS-CUI-03",
            parameters={"method": "network_isolation", "affected_users": 23, "cui_classification": "ITAR"},
            requires_approval=True,
        )
        self.pending_actions["action-002"] = ResponseAction(
            id="action-002",
            action_type="revoke_creds",
            description="Force credential reset for all accounts in the Engineering OU due to potential credential compromise from APT-41 activity. This affects 156 user accounts.",
            risk_level=ActionRisk.CRITICAL,
            target="Engineering OU (156 accounts)",
            parameters={"scope": "engineering_ou", "affected_accounts": 156, "method": "forced_password_reset"},
            requires_approval=True,
        )

        # Seed initial audit entries
        self._add_audit_entry("system", "platform_started", "system", "sovereign", {"version": "0.1.0"})
        self._add_audit_entry("orchestrator-main", "agents_initialized", "agents", "all", {"count": len(self.agents)})
        self._add_audit_entry("compliance-one", "assessment_started", "compliance", "nist-800-171", {"controls": 110})

    def _add_audit_entry(self, actor: str, action: str, resource_type: str, resource_id: str, details: Dict = None) -> AuditEntry:
        """Add an entry to the cryptographic audit trail."""
        import json
        entry_id = generate_event_id()
        entry_data = json.dumps({
            "id": entry_id,
            "actor": actor,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
        }, sort_keys=True)

        chain_hash = compute_chain_hash(entry_data, self._last_audit_hash)

        entry = AuditEntry(
            id=entry_id,
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            hash=chain_hash,
            previous_hash=self._last_audit_hash or "GENESIS",
        )

        self.audit_trail.append(entry)
        self._last_audit_hash = chain_hash
        return entry

    # --- Public API ---

    def add_audit_entry(self, actor: str, action: str, resource_type: str, resource_id: str, details: Dict = None) -> AuditEntry:
        """Thread-safe audit entry creation."""
        with self._lock:
            return self._add_audit_entry(actor, action, resource_type, resource_id, details)

    def get_dashboard_summary(self) -> DashboardSummary:
        """Generate real-time dashboard summary."""
        with self._lock:
            active_threats = [t for t in self.threats.values() if t.status in (ThreatStatus.ACTIVE, ThreatStatus.INVESTIGATING)]
            critical_threats = [t for t in self.threats.values() if t.severity == Severity.CRITICAL and t.status != ThreatStatus.REMEDIATED]
            open_incidents = [i for i in self.incidents.values() if i.status in (IncidentStatus.OPEN, IncidentStatus.INVESTIGATING)]
            running_agents = [a for a in self.agents.values() if a.status == AgentStatus.RUNNING]

            assessed = [c for c in self.controls.values() if c.status != ControlStatus.NOT_ASSESSED]
            compliant = [c for c in self.controls.values() if c.status == ControlStatus.COMPLIANT]
            compliance_score = (len(compliant) / len(self.controls) * 100) if self.controls else 0

            # Compliance by family
            family_stats = {}
            for ctrl in self.controls.values():
                if ctrl.family_id not in family_stats:
                    family_stats[ctrl.family_id] = {"family": ctrl.family, "family_id": ctrl.family_id, "total": 0, "compliant": 0}
                family_stats[ctrl.family_id]["total"] += 1
                if ctrl.status == ControlStatus.COMPLIANT:
                    family_stats[ctrl.family_id]["compliant"] += 1

            compliance_by_family = []
            for fid, stats in sorted(family_stats.items()):
                pct = (stats["compliant"] / stats["total"] * 100) if stats["total"] > 0 else 0
                compliance_by_family.append({
                    "family": stats["family"],
                    "family_id": fid,
                    "total": stats["total"],
                    "compliant": stats["compliant"],
                    "score": round(pct, 1),
                })

            # Threat trend (last 24h, hourly buckets)
            now = datetime.utcnow()
            threat_trend = []
            for hours_ago in range(23, -1, -1):
                bucket_start = now - timedelta(hours=hours_ago + 1)
                bucket_end = now - timedelta(hours=hours_ago)
                count = sum(1 for t in self.threats.values() if bucket_start <= t.detected_at < bucket_end)
                threat_trend.append({
                    "hour": bucket_end.strftime("%H:00"),
                    "threats": count,
                })

            return DashboardSummary(
                total_threats=len(self.threats),
                active_threats=len(active_threats),
                critical_threats=len(critical_threats),
                total_incidents=len(self.incidents),
                open_incidents=len(open_incidents),
                compliance_score=round(compliance_score, 1),
                controls_compliant=len(compliant),
                controls_total=len(self.controls),
                agents_running=len(running_agents),
                agents_total=len(self.agents),
                pending_approvals=len(self.pending_actions),
                last_scan_at=now,
                audit_entries_count=len(self.audit_trail),
                threat_trend=threat_trend,
                compliance_by_family=compliance_by_family,
            )

    def get_threats(self, status: Optional[str] = None, severity: Optional[str] = None) -> List[Threat]:
        """Get threats with optional filtering."""
        with self._lock:
            results = list(self.threats.values())
            if status:
                results = [t for t in results if t.status.value == status]
            if severity:
                results = [t for t in results if t.severity.value == severity]
            return sorted(results, key=lambda t: t.detected_at, reverse=True)

    def get_threat(self, threat_id: str) -> Optional[Threat]:
        with self._lock:
            return self.threats.get(threat_id)

    def get_incidents(self, status: Optional[str] = None) -> List[Incident]:
        with self._lock:
            results = list(self.incidents.values())
            if status:
                results = [i for i in results if i.status.value == status]
            return sorted(results, key=lambda i: i.created_at, reverse=True)

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        with self._lock:
            return self.incidents.get(incident_id)

    def get_controls(self, family_id: Optional[str] = None, status: Optional[str] = None) -> List[ComplianceControl]:
        with self._lock:
            results = list(self.controls.values())
            if family_id:
                results = [c for c in results if c.family_id == family_id]
            if status:
                results = [c for c in results if c.status.value == status]
            return sorted(results, key=lambda c: c.control_id)

    def get_control(self, control_id: str) -> Optional[ComplianceControl]:
        with self._lock:
            return self.controls.get(control_id)

    def get_agents(self) -> List[AgentState]:
        with self._lock:
            return list(self.agents.values())

    def get_agent(self, agent_id: str) -> Optional[AgentState]:
        with self._lock:
            return self.agents.get(agent_id)

    def update_agent_status(self, agent_id: str, status: AgentStatus) -> Optional[AgentState]:
        with self._lock:
            agent = self.agents.get(agent_id)
            if agent:
                agent.status = status
                if status == AgentStatus.RUNNING:
                    agent.started_at = datetime.utcnow()
                self._add_audit_entry(
                    actor="user",
                    action=f"agent_{status.value}",
                    resource_type="agent",
                    resource_id=agent_id,
                    details={"new_status": status.value},
                )
            return agent

    def get_audit_trail(self, limit: int = 50, offset: int = 0) -> List[AuditEntry]:
        with self._lock:
            entries = sorted(self.audit_trail, key=lambda e: e.timestamp, reverse=True)
            return entries[offset:offset + limit]

    def get_pending_actions(self) -> List[ResponseAction]:
        with self._lock:
            return list(self.pending_actions.values())

    def approve_action(self, action_id: str, approved_by: str = "user") -> Optional[ResponseAction]:
        with self._lock:
            action = self.pending_actions.get(action_id)
            if action:
                action.approved = True
                action.approved_by = approved_by
                action.executed = True
                action.executed_at = datetime.utcnow()
                action.result = {"status": "executed", "message": f"Action approved and executed by {approved_by}"}
                del self.pending_actions[action_id]
                self._add_audit_entry(
                    actor=approved_by,
                    action="action_approved",
                    resource_type="response_action",
                    resource_id=action_id,
                    details={"action_type": action.action_type, "target": action.target},
                )
            return action

    def reject_action(self, action_id: str, rejected_by: str = "user") -> Optional[ResponseAction]:
        with self._lock:
            action = self.pending_actions.get(action_id)
            if action:
                action.approved = False
                action.approved_by = rejected_by
                action.result = {"status": "rejected", "message": f"Action rejected by {rejected_by}"}
                del self.pending_actions[action_id]
                self._add_audit_entry(
                    actor=rejected_by,
                    action="action_rejected",
                    resource_type="response_action",
                    resource_id=action_id,
                    details={"action_type": action.action_type, "target": action.target},
                )
            return action

    def respond_to_threat(self, threat_id: str, action: str) -> Optional[Dict]:
        """Execute a response action against a threat."""
        with self._lock:
            threat = self.threats.get(threat_id)
            if not threat:
                return None

            now = datetime.utcnow()
            if action == "contain":
                threat.status = ThreatStatus.CONTAINED
                result = {"status": "contained", "message": f"Threat {threat_id} contained. Network isolation applied to {threat.target_asset}."}
            elif action == "investigate":
                threat.status = ThreatStatus.INVESTIGATING
                result = {"status": "investigating", "message": f"Investigation initiated for threat {threat_id}. Sentinel agents assigned."}
            elif action == "remediate":
                threat.status = ThreatStatus.REMEDIATED
                result = {"status": "remediated", "message": f"Threat {threat_id} remediated. All indicators cleared."}
            elif action == "false_positive":
                threat.status = ThreatStatus.FALSE_POSITIVE
                result = {"status": "false_positive", "message": f"Threat {threat_id} marked as false positive."}
            else:
                return {"error": f"Unknown action: {action}"}

            threat.updated_at = now
            self._add_audit_entry(
                actor="user",
                action=f"threat_{action}",
                resource_type="threat",
                resource_id=threat_id,
                details={"action": action, "previous_status": threat.status.value},
            )
            return result

    def run_compliance_assessment(self) -> Dict:
        """Trigger a new compliance assessment cycle."""
        with self._lock:
            now = datetime.utcnow()
            assessed_count = 0
            for control in self.controls.values():
                control.last_assessed = now
                control.assessor = "compliance-one"
                assessed_count += 1

            self._add_audit_entry(
                actor="compliance-one",
                action="assessment_completed",
                resource_type="compliance",
                resource_id="nist-800-171",
                details={"controls_assessed": assessed_count},
            )

            compliant = sum(1 for c in self.controls.values() if c.status == ControlStatus.COMPLIANT)
            return {
                "status": "completed",
                "controls_assessed": assessed_count,
                "compliant": compliant,
                "compliance_score": round(compliant / len(self.controls) * 100, 1),
                "assessed_at": now.isoformat(),
            }


# Singleton instance
platform_state = PlatformState()
