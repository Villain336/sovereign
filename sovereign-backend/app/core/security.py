"""Security utilities for Sovereign platform."""

import hashlib
import hmac
import secrets
import time
from typing import Optional


def generate_event_id() -> str:
    """Generate a unique event ID with timestamp prefix."""
    timestamp = int(time.time() * 1000)
    random_part = secrets.token_hex(8)
    return f"evt-{timestamp}-{random_part}"


def generate_agent_id(agent_type: str) -> str:
    """Generate a unique agent ID."""
    random_part = secrets.token_hex(4)
    return f"{agent_type}-{random_part}"


def compute_hash(data: str, algorithm: str = "sha256") -> str:
    """Compute cryptographic hash of data."""
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode("utf-8"))
    return hasher.hexdigest()


def compute_chain_hash(current_data: str, previous_hash: Optional[str], algorithm: str = "sha256") -> str:
    """Compute a chained hash for append-only audit trail integrity."""
    chain_input = f"{previous_hash or 'GENESIS'}:{current_data}"
    return compute_hash(chain_input, algorithm)


def verify_chain_hash(current_data: str, previous_hash: Optional[str], expected_hash: str, algorithm: str = "sha256") -> bool:
    """Verify a chain hash for audit trail integrity."""
    computed = compute_chain_hash(current_data, previous_hash, algorithm)
    return hmac.compare_digest(computed, expected_hash)
