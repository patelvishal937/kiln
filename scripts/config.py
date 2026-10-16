"""Kiln settings.

Kiln runs INSIDE a Claude Code / Codex session. There is no model API key here:
the agent IS the model, and the MCP servers (Greta, Apify, Volanea, Higgsfield...)
are whatever that session has connected. This module only holds:
  - where runs and prompts live,
  - optional keys the Python *helper scripts* need (HeyGen REST, S3 upload),
  - the budget/growth numbers the policy references.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # dotenv is optional; env vars still work without it
    def load_dotenv(*_a, **_k):  # type: ignore
        return False

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "references" / "phases"
RUNS_DIR = ROOT / "runs"
REMOTION_DIR = ROOT / "remotion"

load_dotenv(ROOT / ".env")


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _num(name: str, default: float) -> float:
    raw = _env(name)
    return float(raw) if raw else default


@dataclass(frozen=True)
class Settings:
    # Greta target is informational only — the session already holds the connection.
    greta_url: str = field(default_factory=lambda: _env("GRETA_MCP_URL", "https://staging-mcp.greta.sh/mcp"))

    run_credit_cap: float = field(default_factory=lambda: _num("RUN_CREDIT_CAP", 150))
    per_call_credit_cap: float = field(default_factory=lambda: _num("PER_CALL_CREDIT_CAP", 25))
    growth_nightly_credit_limit: float = field(default_factory=lambda: _num("GROWTH_NIGHTLY_CREDIT_LIMIT", 10))
    growth_tasks_per_night: int = field(default_factory=lambda: int(_num("GROWTH_TASKS_PER_NIGHT", 2)))
    timezone: str = field(default_factory=lambda: _env("TIMEZONE", "Asia/Kolkata"))

    # Helper-script integrations (the agent uses MCP for the rest).
    heygen_key: str = field(default_factory=lambda: _env("HEYGEN_API_KEY"))
    heygen_avatar_id: str = field(default_factory=lambda: _env("HEYGEN_AVATAR_ID"))
    heygen_voice_id: str = field(default_factory=lambda: _env("HEYGEN_VOICE_ID"))

    s3_bucket: str = field(default_factory=lambda: _env("ASSET_S3_BUCKET"))
    s3_prefix: str = field(default_factory=lambda: _env("ASSET_S3_PREFIX", "kiln"))
    s3_endpoint: str = field(default_factory=lambda: _env("ASSET_S3_ENDPOINT_URL"))
    asset_public_base: str = field(default_factory=lambda: _env("ASSET_PUBLIC_BASE_URL"))

    @property
    def has_heygen(self) -> bool:
        return bool(self.heygen_key and self.heygen_avatar_id and self.heygen_voice_id)

    @property
    def has_s3(self) -> bool:
        return bool(self.s3_bucket and self.asset_public_base)

    @property
    def has_remotion(self) -> bool:
        return shutil.which("npx") is not None and (REMOTION_DIR / "node_modules").exists()

    def integrations_summary(self) -> dict[str, bool]:
        return {
            "heygen": self.has_heygen,
            "s3_upload": self.has_s3,
            "remotion": self.has_remotion,
            "playwright": _module_present("playwright"),
        }


def _module_present(name: str) -> bool:
    import importlib.util

    return importlib.util.find_spec(name) is not None
