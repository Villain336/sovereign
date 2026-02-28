from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import actions, agents, audit, compliance, dashboard, incidents, threats

app = FastAPI(
    title="Sovereign",
    description="Agentic Cyber Defense & Compliance Platform for the Defense Industrial Base",
    version="0.1.0",
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Register routers
app.include_router(dashboard.router)
app.include_router(threats.router)
app.include_router(incidents.router)
app.include_router(compliance.router)
app.include_router(agents.router)
app.include_router(audit.router)
app.include_router(actions.router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/info")
async def platform_info():
    """Platform information and version."""
    return {
        "name": "Sovereign",
        "version": "0.1.0",
        "description": "Agentic Cyber Defense & Compliance Platform",
        "compliance_framework": "NIST 800-171 Rev 2 / CMMC Level 2",
        "agent_types": ["sentinel", "vanguard", "compliance", "orchestrator"],
        "features": [
            "Autonomous threat detection (MITRE ATT&CK mapped)",
            "Automated incident response with human-in-the-loop",
            "Continuous CMMC Level 2 compliance monitoring (110 controls)",
            "Cryptographic append-only audit trail",
            "Multi-agent orchestration engine",
        ],
    }
