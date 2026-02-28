"""Complete NIST 800-171 Rev 2 control definitions for CMMC Level 2.

All 110 controls across 14 families, mapped to CMMC Level 2 requirements.
"""

from typing import Dict, List

# Control family definitions
CONTROL_FAMILIES: Dict[str, str] = {
    "AC": "Access Control",
    "AT": "Awareness and Training",
    "AU": "Audit and Accountability",
    "CM": "Configuration Management",
    "IA": "Identification and Authentication",
    "IR": "Incident Response",
    "MA": "Maintenance",
    "MP": "Media Protection",
    "PE": "Physical Protection",
    "PS": "Personnel Security",
    "RA": "Risk Assessment",
    "CA": "Security Assessment",
    "SC": "System and Communications Protection",
    "SI": "System and Information Integrity",
}

# All 110 NIST 800-171 Rev 2 controls
NIST_800_171_CONTROLS: List[Dict[str, str]] = [
    # Access Control (AC) - 22 controls
    {"id": "3.1.1", "family": "AC", "title": "Limit system access to authorized users, processes acting on behalf of authorized users, and devices (including other systems).", "description": "Access control policies control access between active entities or subjects and passive entities or objects in systems. Enforce authorized access at the system level."},
    {"id": "3.1.2", "family": "AC", "title": "Limit system access to the types of transactions and functions that authorized users are permitted to execute.", "description": "Limit and control system access based on the types of transactions and functions that authorized users are permitted to execute."},
    {"id": "3.1.3", "family": "AC", "title": "Control the flow of CUI in accordance with approved authorizations.", "description": "Information flow control regulates where CUI can travel within a system and between systems."},
    {"id": "3.1.4", "family": "AC", "title": "Separate the duties of individuals to reduce the risk of malevolent activity without collusion.", "description": "Separation of duties addresses the potential for abuse of authorized privileges."},
    {"id": "3.1.5", "family": "AC", "title": "Employ the principle of least privilege, including for specific security functions and privileged accounts.", "description": "Employ the principle of least privilege, allowing only authorized accesses for users and processes."},
    {"id": "3.1.6", "family": "AC", "title": "Use non-privileged accounts or roles when accessing nonsecurity functions.", "description": "Require that users of system accounts or roles with access to security functions use non-privileged accounts when accessing nonsecurity functions."},
    {"id": "3.1.7", "family": "AC", "title": "Prevent non-privileged users from executing privileged functions and capture the execution of such functions in audit logs.", "description": "Privileged functions include establishing system accounts, performing system integrity checks, conducting patching operations, or administering cryptographic key management activities."},
    {"id": "3.1.8", "family": "AC", "title": "Limit unsuccessful logon attempts.", "description": "Enforce a limit of consecutive invalid logon attempts by a user during a defined time period. Automatically lock the account or node for a specified time period or until released by an administrator."},
    {"id": "3.1.9", "family": "AC", "title": "Provide privacy and security notices consistent with applicable CUI rules.", "description": "System use notifications can be implemented using messages or warning banners displayed before individuals log in to systems."},
    {"id": "3.1.10", "family": "AC", "title": "Use session lock with pattern-hiding displays to prevent access and viewing of data after a period of inactivity.", "description": "Session locks are temporary actions taken when users stop work and move away from the immediate vicinity of the system."},
    {"id": "3.1.11", "family": "AC", "title": "Terminate (automatically) a user session after a defined condition.", "description": "Automatic session termination addresses the termination of user-initiated logical sessions in contrast to session lock."},
    {"id": "3.1.12", "family": "AC", "title": "Monitor and control remote access sessions.", "description": "Remote access is access to systems by users communicating through external networks. Automated monitoring and control of remote access sessions allows organizations to detect cyber attacks."},
    {"id": "3.1.13", "family": "AC", "title": "Employ cryptographic mechanisms to protect the confidentiality of remote access sessions.", "description": "Cryptographic standards include FIPS-validated cryptography and NSA-approved cryptography."},
    {"id": "3.1.14", "family": "AC", "title": "Route remote access via managed access control points.", "description": "Routing remote access through managed access control points enhances explicit, organizational control over such connections."},
    {"id": "3.1.15", "family": "AC", "title": "Authorize remote execution of privileged commands and remote access to security-relevant information.", "description": "Authorize the remote execution of privileged commands and the remote access to security-relevant information."},
    {"id": "3.1.16", "family": "AC", "title": "Authorize wireless access prior to allowing such connections.", "description": "Establishing usage restrictions and configuration/connection requirements for wireless access."},
    {"id": "3.1.17", "family": "AC", "title": "Protect wireless access using authentication and encryption.", "description": "Protect wireless access to the system using authentication and encryption."},
    {"id": "3.1.18", "family": "AC", "title": "Control connection of mobile devices.", "description": "Establish usage restrictions, configuration requirements, connection requirements, and implementation guidance for organization-controlled mobile devices."},
    {"id": "3.1.19", "family": "AC", "title": "Encrypt CUI on mobile devices and mobile computing platforms.", "description": "Employ full-device encryption or container encryption to protect the confidentiality of CUI on mobile devices."},
    {"id": "3.1.20", "family": "AC", "title": "Verify and control/limit connections to and use of external systems.", "description": "External systems are systems or components of systems for which organizations typically have no direct supervision and authority."},
    {"id": "3.1.21", "family": "AC", "title": "Limit use of portable storage devices on external systems.", "description": "Limits on the use of organization-controlled portable storage devices in external systems."},
    {"id": "3.1.22", "family": "AC", "title": "Control CUI posted or processed on publicly accessible systems.", "description": "Control information posted or processed on publicly accessible systems."},

    # Awareness and Training (AT) - 3 controls
    {"id": "3.2.1", "family": "AT", "title": "Ensure that managers, systems administrators, and users of organizational systems are made aware of the security risks associated with their activities and of the applicable policies, standards, and procedures related to the security of those systems.", "description": "Awareness and training measures for organizational personnel."},
    {"id": "3.2.2", "family": "AT", "title": "Ensure that personnel are trained to carry out their assigned information security-related duties and responsibilities.", "description": "Training for organizational personnel with assigned security roles and responsibilities."},
    {"id": "3.2.3", "family": "AT", "title": "Provide security awareness training on recognizing and reporting potential indicators of insider threat.", "description": "Insider threat awareness training for organizational personnel."},

    # Audit and Accountability (AU) - 9 controls
    {"id": "3.3.1", "family": "AU", "title": "Create and retain system audit logs and records to the extent needed to enable the monitoring, analysis, investigation, and reporting of unlawful or unauthorized system activity.", "description": "Create, protect, and retain audit records."},
    {"id": "3.3.2", "family": "AU", "title": "Ensure that the actions of individual system users can be uniquely traced to those users so they can be held accountable for their actions.", "description": "Content of audit records includes user identity information."},
    {"id": "3.3.3", "family": "AU", "title": "Review and update logged events.", "description": "Review and update the events to be logged on a regular basis."},
    {"id": "3.3.4", "family": "AU", "title": "Alert in the event of an audit logging process failure.", "description": "Provide alerts to appropriate personnel in the event of an audit logging process failure."},
    {"id": "3.3.5", "family": "AU", "title": "Correlate audit record review, analysis, and reporting processes to support organizational processes for investigation and response to suspicious activities.", "description": "Correlating audit record review, analysis, and reporting processes."},
    {"id": "3.3.6", "family": "AU", "title": "Provide audit record reduction and report generation to support on-demand analysis and reporting.", "description": "Audit record reduction and report generation capability."},
    {"id": "3.3.7", "family": "AU", "title": "Provide a system capability that compares and synchronizes internal system clocks with an authoritative source to generate time stamps for audit records.", "description": "Time stamps generated by the system include date and time, synchronized to an authoritative time source."},
    {"id": "3.3.8", "family": "AU", "title": "Protect audit information and audit logging tools from unauthorized access, modification, and deletion.", "description": "Protection of audit information."},
    {"id": "3.3.9", "family": "AU", "title": "Limit management of audit logging functionality to a subset of privileged users.", "description": "Restricting the management of audit logging functionality."},

    # Configuration Management (CM) - 9 controls
    {"id": "3.4.1", "family": "CM", "title": "Establish and maintain baseline configurations and inventories of organizational systems (including hardware, software, firmware, and documentation) throughout the respective system development life cycles.", "description": "Baseline configurations for systems and system components."},
    {"id": "3.4.2", "family": "CM", "title": "Establish and enforce security configuration settings for information technology products employed in organizational systems.", "description": "Security-focused configuration settings for IT products."},
    {"id": "3.4.3", "family": "CM", "title": "Track, review, approve or disapprove, and log changes to organizational systems.", "description": "Configuration change control processes."},
    {"id": "3.4.4", "family": "CM", "title": "Analyze the security impact of changes prior to implementation.", "description": "Security impact analysis for organizational changes."},
    {"id": "3.4.5", "family": "CM", "title": "Define, document, approve, and enforce physical and logical access restrictions associated with changes to organizational systems.", "description": "Access restrictions for change management."},
    {"id": "3.4.6", "family": "CM", "title": "Employ the principle of least functionality by configuring organizational systems to provide only essential capabilities.", "description": "Least functionality configuration."},
    {"id": "3.4.7", "family": "CM", "title": "Restrict, disable, or prevent the use of nonessential programs, functions, ports, protocols, and services.", "description": "Restriction of nonessential functionality."},
    {"id": "3.4.8", "family": "CM", "title": "Apply deny-by-exception (blacklisting) policy to prevent the use of unauthorized software or deny-all, permit-by-exception (whitelisting) policy to allow the execution of authorized software.", "description": "Application whitelisting/blacklisting."},
    {"id": "3.4.9", "family": "CM", "title": "Control and monitor user-installed software.", "description": "Control and monitoring of user-installed software."},

    # Identification and Authentication (IA) - 11 controls
    {"id": "3.5.1", "family": "IA", "title": "Identify system users, processes acting on behalf of users, and devices.", "description": "Uniquely identify system users, processes acting on behalf of users, and devices."},
    {"id": "3.5.2", "family": "IA", "title": "Authenticate (or verify) the identities of users, processes, or devices, as a prerequisite to allowing access to organizational systems.", "description": "Authentication of users, processes, or devices."},
    {"id": "3.5.3", "family": "IA", "title": "Use multifactor authentication for local and network access to privileged accounts and for network access to non-privileged accounts.", "description": "Multi-factor authentication implementation."},
    {"id": "3.5.4", "family": "IA", "title": "Employ replay-resistant authentication mechanisms for network access to privileged and non-privileged accounts.", "description": "Replay-resistant authentication mechanisms."},
    {"id": "3.5.5", "family": "IA", "title": "Prevent reuse of identifiers for a defined period.", "description": "Identifier management preventing reuse."},
    {"id": "3.5.6", "family": "IA", "title": "Disable identifiers after a defined period of inactivity.", "description": "Disabling inactive identifiers."},
    {"id": "3.5.7", "family": "IA", "title": "Enforce a minimum password complexity and change of characters when new passwords are created.", "description": "Password complexity requirements."},
    {"id": "3.5.8", "family": "IA", "title": "Prohibit password reuse for a specified number of generations.", "description": "Password reuse restrictions."},
    {"id": "3.5.9", "family": "IA", "title": "Allow temporary password use for system logons with an immediate change to a permanent password.", "description": "Temporary password management."},
    {"id": "3.5.10", "family": "IA", "title": "Store and transmit only cryptographically-protected passwords.", "description": "Cryptographic protection of passwords."},
    {"id": "3.5.11", "family": "IA", "title": "Obscure feedback of authentication information.", "description": "Authentication feedback obscuring."},

    # Incident Response (IR) - 3 controls
    {"id": "3.6.1", "family": "IR", "title": "Establish an operational incident-handling capability for organizational systems that includes preparation, detection, analysis, containment, recovery, and user response activities.", "description": "Incident handling capability establishment."},
    {"id": "3.6.2", "family": "IR", "title": "Track, document, and report incidents to designated officials and/or authorities both internal and external to the organization.", "description": "Incident tracking, documenting, and reporting."},
    {"id": "3.6.3", "family": "IR", "title": "Test the organizational incident response capability.", "description": "Incident response testing."},

    # Maintenance (MA) - 6 controls
    {"id": "3.7.1", "family": "MA", "title": "Perform maintenance on organizational systems.", "description": "System maintenance activities."},
    {"id": "3.7.2", "family": "MA", "title": "Provide controls on the tools, techniques, mechanisms, and personnel used to conduct system maintenance.", "description": "Controlled maintenance activities."},
    {"id": "3.7.3", "family": "MA", "title": "Ensure equipment removed for off-site maintenance is sanitized of any CUI.", "description": "Equipment sanitization for off-site maintenance."},
    {"id": "3.7.4", "family": "MA", "title": "Check media containing diagnostic and test programs for malicious code before the media are used in organizational systems.", "description": "Media inspection before use."},
    {"id": "3.7.5", "family": "MA", "title": "Require multifactor authentication to establish nonlocal maintenance sessions via external network connections and terminate such connections when nonlocal maintenance is complete.", "description": "Nonlocal maintenance MFA requirements."},
    {"id": "3.7.6", "family": "MA", "title": "Supervise the maintenance activities of maintenance personnel without required access authorization.", "description": "Maintenance personnel supervision."},

    # Media Protection (MP) - 9 controls
    {"id": "3.8.1", "family": "MP", "title": "Protect (i.e., physically control and securely store) system media containing CUI, both paper and digital.", "description": "Physical media protection."},
    {"id": "3.8.2", "family": "MP", "title": "Limit access to CUI on system media to authorized users.", "description": "Media access limitations."},
    {"id": "3.8.3", "family": "MP", "title": "Sanitize or destroy system media containing CUI before disposal or release for reuse.", "description": "Media sanitization."},
    {"id": "3.8.4", "family": "MP", "title": "Mark media with necessary CUI markings and distribution limitations.", "description": "Media marking requirements."},
    {"id": "3.8.5", "family": "MP", "title": "Control access to media containing CUI and maintain accountability for media during transport outside of controlled areas.", "description": "Media transport protection."},
    {"id": "3.8.6", "family": "MP", "title": "Implement cryptographic mechanisms to protect the confidentiality of CUI stored on digital media during transport unless otherwise protected by alternative physical safeguards.", "description": "Cryptographic protection of transported media."},
    {"id": "3.8.7", "family": "MP", "title": "Control the use of removable media on system components.", "description": "Removable media usage control."},
    {"id": "3.8.8", "family": "MP", "title": "Prohibit the use of portable storage devices when such devices have no identifiable owner.", "description": "Portable storage device restrictions."},
    {"id": "3.8.9", "family": "MP", "title": "Protect the confidentiality of backup CUI at storage locations.", "description": "Backup CUI confidentiality."},

    # Physical Protection (PE) - 6 controls
    {"id": "3.10.1", "family": "PE", "title": "Limit physical access to organizational systems, equipment, and the respective operating environments to authorized individuals.", "description": "Physical access control."},
    {"id": "3.10.2", "family": "PE", "title": "Protect and monitor the physical facility and support infrastructure for organizational systems.", "description": "Physical facility monitoring."},
    {"id": "3.10.3", "family": "PE", "title": "Escort visitors and monitor visitor activity.", "description": "Visitor escort and monitoring."},
    {"id": "3.10.4", "family": "PE", "title": "Maintain audit logs of physical access.", "description": "Physical access audit logs."},
    {"id": "3.10.5", "family": "PE", "title": "Control and manage physical access devices.", "description": "Physical access device management."},
    {"id": "3.10.6", "family": "PE", "title": "Enforce safeguarding measures for CUI at alternate work sites.", "description": "Alternate work site safeguards."},

    # Personnel Security (PS) - 2 controls
    {"id": "3.9.1", "family": "PS", "title": "Screen individuals prior to authorizing access to organizational systems containing CUI.", "description": "Personnel screening."},
    {"id": "3.9.2", "family": "PS", "title": "Ensure that organizational systems containing CUI are protected during and after personnel actions such as terminations and transfers.", "description": "Personnel action protections."},

    # Risk Assessment (RA) - 3 controls
    {"id": "3.11.1", "family": "RA", "title": "Periodically assess the risk to organizational operations, organizational assets, and individuals, resulting from the operation of organizational systems and the associated processing, storage, or transmission of CUI.", "description": "Risk assessment processes."},
    {"id": "3.11.2", "family": "RA", "title": "Scan for vulnerabilities in organizational systems and applications periodically and when new vulnerabilities affecting those systems and applications are identified.", "description": "Vulnerability scanning."},
    {"id": "3.11.3", "family": "RA", "title": "Remediate vulnerabilities in accordance with risk assessments.", "description": "Vulnerability remediation."},

    # Security Assessment (CA) - 4 controls
    {"id": "3.12.1", "family": "CA", "title": "Periodically assess the security controls in organizational systems to determine if the controls are effective in their application.", "description": "Security control assessment."},
    {"id": "3.12.2", "family": "CA", "title": "Develop and implement plans of action designed to correct deficiencies and reduce or eliminate vulnerabilities in organizational systems.", "description": "Plan of Action and Milestones (POA&M)."},
    {"id": "3.12.3", "family": "CA", "title": "Monitor security controls on an ongoing basis to ensure the continued effectiveness of the controls.", "description": "Continuous monitoring."},
    {"id": "3.12.4", "family": "CA", "title": "Develop, document, and periodically update system security plans that describe system boundaries, system environments of operation, how security requirements are implemented, and the relationships with or connections to other systems.", "description": "System Security Plan (SSP)."},

    # System and Communications Protection (SC) - 16 controls
    {"id": "3.13.1", "family": "SC", "title": "Monitor, control, and protect communications (i.e., information transmitted or received by organizational systems) at the external boundaries and key internal boundaries of organizational systems.", "description": "Boundary protection."},
    {"id": "3.13.2", "family": "SC", "title": "Employ architectural designs, software development techniques, and systems engineering principles that promote effective information security within organizational systems.", "description": "Security engineering principles."},
    {"id": "3.13.3", "family": "SC", "title": "Separate user functionality from system management functionality.", "description": "User/management functionality separation."},
    {"id": "3.13.4", "family": "SC", "title": "Prevent unauthorized and unintended information transfer via shared system resources.", "description": "Shared resource control."},
    {"id": "3.13.5", "family": "SC", "title": "Implement subnetworks for publicly accessible system components that are physically or logically separated from internal networks.", "description": "Public access subnetwork separation (DMZ)."},
    {"id": "3.13.6", "family": "SC", "title": "Deny network communications traffic by default and allow network communications traffic by exception (i.e., deny all, permit by exception).", "description": "Deny-by-default network policy."},
    {"id": "3.13.7", "family": "SC", "title": "Prevent remote devices from simultaneously establishing non-remote connections with organizational systems and communicating via some other connection to resources in external networks (i.e., split tunneling).", "description": "Split tunneling prevention."},
    {"id": "3.13.8", "family": "SC", "title": "Implement cryptographic mechanisms to prevent unauthorized disclosure of CUI during transmission unless otherwise protected by alternative physical safeguards.", "description": "Transmission confidentiality."},
    {"id": "3.13.9", "family": "SC", "title": "Terminate network connections associated with communications sessions at the end of the sessions or after a defined period of inactivity.", "description": "Session termination."},
    {"id": "3.13.10", "family": "SC", "title": "Establish and manage cryptographic keys for cryptography employed in organizational systems.", "description": "Cryptographic key management."},
    {"id": "3.13.11", "family": "SC", "title": "Employ FIPS-validated cryptography when used to protect the confidentiality of CUI.", "description": "FIPS-validated cryptography."},
    {"id": "3.13.12", "family": "SC", "title": "Prohibit remote activation of collaborative computing devices and provide indication of devices in use to users present at the device.", "description": "Collaborative computing device control."},
    {"id": "3.13.13", "family": "SC", "title": "Control and monitor the use of mobile code.", "description": "Mobile code control."},
    {"id": "3.13.14", "family": "SC", "title": "Control and monitor the use of Voice over Internet Protocol (VoIP) technologies.", "description": "VoIP security."},
    {"id": "3.13.15", "family": "SC", "title": "Protect the authenticity of communications sessions.", "description": "Session authenticity."},
    {"id": "3.13.16", "family": "SC", "title": "Protect the confidentiality of CUI at rest.", "description": "Data-at-rest protection."},

    # System and Information Integrity (SI) - 7 controls
    {"id": "3.14.1", "family": "SI", "title": "Identify, report, and correct system flaws in a timely manner.", "description": "Flaw remediation."},
    {"id": "3.14.2", "family": "SI", "title": "Provide protection from malicious code at designated locations within organizational systems.", "description": "Malicious code protection."},
    {"id": "3.14.3", "family": "SI", "title": "Monitor system security alerts and advisories and take action in response.", "description": "Security alert monitoring."},
    {"id": "3.14.4", "family": "SI", "title": "Update malicious code protection mechanisms when new releases are available.", "description": "Malicious code protection updates."},
    {"id": "3.14.5", "family": "SI", "title": "Perform periodic scans of organizational systems and real-time scans of files from external sources as files are downloaded, opened, or executed.", "description": "System and file scanning."},
    {"id": "3.14.6", "family": "SI", "title": "Monitor organizational systems, including inbound and outbound communications traffic, to detect attacks and indicators of potential attacks.", "description": "System monitoring."},
    {"id": "3.14.7", "family": "SI", "title": "Identify unauthorized use of organizational systems.", "description": "Unauthorized use identification."},
]

# MITRE ATT&CK technique database for threat mapping
MITRE_ATTACK_TECHNIQUES: List[Dict[str, str]] = [
    {"id": "T1566", "name": "Phishing", "tactic": "Initial Access", "description": "Adversaries may send phishing messages to gain access to victim systems."},
    {"id": "T1566.001", "name": "Spearphishing Attachment", "tactic": "Initial Access", "description": "Adversaries may send spearphishing emails with a malicious attachment."},
    {"id": "T1566.002", "name": "Spearphishing Link", "tactic": "Initial Access", "description": "Adversaries may send spearphishing emails with a malicious link."},
    {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "Initial Access", "description": "Adversaries may attempt to exploit a weakness in an Internet-facing application."},
    {"id": "T1133", "name": "External Remote Services", "tactic": "Initial Access", "description": "Adversaries may leverage external-facing remote services to initially access a network."},
    {"id": "T1078", "name": "Valid Accounts", "tactic": "Defense Evasion", "description": "Adversaries may obtain and abuse credentials of existing accounts."},
    {"id": "T1078.001", "name": "Default Accounts", "tactic": "Defense Evasion", "description": "Adversaries may obtain and abuse credentials of a default account."},
    {"id": "T1059", "name": "Command and Scripting Interpreter", "tactic": "Execution", "description": "Adversaries may abuse command and script interpreters to execute commands."},
    {"id": "T1059.001", "name": "PowerShell", "tactic": "Execution", "description": "Adversaries may abuse PowerShell commands and scripts for execution."},
    {"id": "T1059.003", "name": "Windows Command Shell", "tactic": "Execution", "description": "Adversaries may abuse the Windows command shell for execution."},
    {"id": "T1053", "name": "Scheduled Task/Job", "tactic": "Execution", "description": "Adversaries may abuse task scheduling functionality to facilitate execution."},
    {"id": "T1547", "name": "Boot or Logon Autostart Execution", "tactic": "Persistence", "description": "Adversaries may configure system settings to automatically execute a program during system boot or logon."},
    {"id": "T1136", "name": "Create Account", "tactic": "Persistence", "description": "Adversaries may create an account to maintain access to victim systems."},
    {"id": "T1098", "name": "Account Manipulation", "tactic": "Persistence", "description": "Adversaries may manipulate accounts to maintain access to victim systems."},
    {"id": "T1548", "name": "Abuse Elevation Control Mechanism", "tactic": "Privilege Escalation", "description": "Adversaries may circumvent mechanisms designed to control elevate privileges."},
    {"id": "T1068", "name": "Exploitation for Privilege Escalation", "tactic": "Privilege Escalation", "description": "Adversaries may exploit software vulnerabilities to escalate privileges."},
    {"id": "T1562", "name": "Impair Defenses", "tactic": "Defense Evasion", "description": "Adversaries may maliciously modify components of a victim environment to hinder defenses."},
    {"id": "T1070", "name": "Indicator Removal", "tactic": "Defense Evasion", "description": "Adversaries may delete or modify artifacts generated within systems to remove evidence."},
    {"id": "T1110", "name": "Brute Force", "tactic": "Credential Access", "description": "Adversaries may use brute force techniques to gain access to accounts."},
    {"id": "T1003", "name": "OS Credential Dumping", "tactic": "Credential Access", "description": "Adversaries may attempt to dump credentials to obtain account login information."},
    {"id": "T1087", "name": "Account Discovery", "tactic": "Discovery", "description": "Adversaries may attempt to get a listing of accounts on a system or within an environment."},
    {"id": "T1046", "name": "Network Service Discovery", "tactic": "Discovery", "description": "Adversaries may attempt to get a listing of services running on remote hosts."},
    {"id": "T1021", "name": "Remote Services", "tactic": "Lateral Movement", "description": "Adversaries may use valid accounts to log into a service specifically designed to accept remote connections."},
    {"id": "T1570", "name": "Lateral Tool Transfer", "tactic": "Lateral Movement", "description": "Adversaries may transfer tools or other files between systems in a compromised environment."},
    {"id": "T1560", "name": "Archive Collected Data", "tactic": "Collection", "description": "Adversaries may compress and/or encrypt data that is collected prior to exfiltration."},
    {"id": "T1005", "name": "Data from Local System", "tactic": "Collection", "description": "Adversaries may search local system sources to find files of interest and sensitive data."},
    {"id": "T1041", "name": "Exfiltration Over C2 Channel", "tactic": "Exfiltration", "description": "Adversaries may steal data by exfiltrating it over an existing command and control channel."},
    {"id": "T1048", "name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration", "description": "Adversaries may steal data by exfiltrating it over a different protocol than the existing C2 channel."},
    {"id": "T1071", "name": "Application Layer Protocol", "tactic": "Command and Control", "description": "Adversaries may communicate using application layer protocols to avoid detection."},
    {"id": "T1105", "name": "Ingress Tool Transfer", "tactic": "Command and Control", "description": "Adversaries may transfer tools or other files from an external system into a compromised environment."},
    {"id": "T1486", "name": "Data Encrypted for Impact", "tactic": "Impact", "description": "Adversaries may encrypt data on target systems to interrupt availability."},
    {"id": "T1489", "name": "Service Stop", "tactic": "Impact", "description": "Adversaries may stop or disable services on a system to render those services unavailable."},
    {"id": "T1195", "name": "Supply Chain Compromise", "tactic": "Initial Access", "description": "Adversaries may manipulate products or product delivery mechanisms prior to receipt by a final consumer."},
    {"id": "T1199", "name": "Trusted Relationship", "tactic": "Initial Access", "description": "Adversaries may breach or otherwise leverage organizations who have access to intended victims."},
    {"id": "T1556", "name": "Modify Authentication Process", "tactic": "Credential Access", "description": "Adversaries may modify authentication mechanisms and processes to access user credentials."},
]


def get_all_controls() -> List[Dict[str, str]]:
    """Return all 110 NIST 800-171 controls."""
    return NIST_800_171_CONTROLS


def get_controls_by_family(family_id: str) -> List[Dict[str, str]]:
    """Return controls for a specific family."""
    return [c for c in NIST_800_171_CONTROLS if c["family"] == family_id]


def get_control_by_id(control_id: str) -> Dict[str, str] | None:
    """Return a specific control by ID."""
    for control in NIST_800_171_CONTROLS:
        if control["id"] == control_id:
            return control
    return None


def get_mitre_technique(technique_id: str) -> Dict[str, str] | None:
    """Return a specific MITRE ATT&CK technique by ID."""
    for technique in MITRE_ATTACK_TECHNIQUES:
        if technique["id"] == technique_id:
            return technique
    return None
