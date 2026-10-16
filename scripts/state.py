"""Run state: one folder per run, resumable, with an append-only event log."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from config import RUNS_DIR

PhaseStatus = Literal["pending", "running", "done", "skipped", "failed"]


class PhaseRecord(BaseModel):
    status: PhaseStatus = "pending"
    output: dict[str, Any] | None = None
    note: str = ""
    started_at: float | None = None
    finished_at: float | None = None
    claude_cost_usd: float = 0.0
    attempts: int = 0


class RunState(BaseModel):
    run_id: str
    idea: str
    source_kind: str = "idea"  # idea | website | apk
    source_ref: str = ""  # url or file path when reverse-engineering
    created_at: float = Field(default_factory=time.time)
    auto: bool = False
    phases: dict[str, PhaseRecord] = {}
    greta_credits_committed: float = 0.0  # upper bound: sum of creditBudgets allowed
    human_todos: list[str] = []
    notes: list[str] = []

    # ------------------------------------------------------------------ paths
    @property
    def dir(self) -> Path:
        return RUNS_DIR / self.run_id

    @property
    def assets_dir(self) -> Path:
        p = self.dir / "assets"
        p.mkdir(parents=True, exist_ok=True)
        return p

    # ---------------------------------------------------------------- helpers
    def phase(self, name: str) -> PhaseRecord:
        return self.phases.setdefault(name, PhaseRecord())

    def output(self, name: str) -> dict[str, Any] | None:
        rec = self.phases.get(name)
        return rec.output if rec and rec.status == "done" else None

    def add_todos(self, todos: list[str]) -> None:
        for t in todos:
            if t and t not in self.human_todos:
                self.human_todos.append(t)

    def save(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        tmp = self.dir / "state.json.tmp"
        tmp.write_text(self.model_dump_json(indent=2))
        tmp.replace(self.dir / "state.json")

    def log(self, event: str, **data: Any) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        line = {"t": round(time.time(), 2), "event": event, **data}
        with (self.dir / "events.jsonl").open("a") as f:
            f.write(json.dumps(line, default=str)[:20000] + "\n")

    def reserve_credits(self, amount: float, per_call_cap: float, run_cap: float) -> tuple[bool, str]:
        """Policy gate the agent calls before each Greta send/deploy. Does NOT persist on refusal."""
        if amount > per_call_cap:
            return False, f"creditBudget {amount} exceeds the per-call cap {per_call_cap}; split the work smaller."
        if self.greta_credits_committed + amount > run_cap:
            return False, (f"run credit cap {run_cap} would be exceeded "
                           f"(already committed {self.greta_credits_committed}). Stop building and submit with open_issues.")
        self.greta_credits_committed += amount
        self.save()
        return True, f"reserved {amount}; committed {self.greta_credits_committed}/{run_cap}."

    # ------------------------------------------------------------ constructors
    @classmethod
    def new(cls, idea: str, auto: bool, source_kind: str = "idea", source_ref: str = "") -> "RunState":
        base = re.sub(r"^https?://(www\.)?", "", source_ref) if source_ref else idea
        slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:32] or "run"
        run_id = f"{slug}-{datetime.now():%Y%m%d-%H%M}"
        state = cls(run_id=run_id, idea=idea, auto=auto, source_kind=source_kind, source_ref=source_ref)
        state.save()
        _set_current(run_id)
        return state

    @classmethod
    def load(cls, run_id: str) -> "RunState":
        path = RUNS_DIR / run_id / "state.json"
        if not path.exists():
            raise SystemExit(f"No run named {run_id!r} under {RUNS_DIR}")
        return cls.model_validate_json(path.read_text())

    @classmethod
    def current(cls) -> "RunState":
        ptr = RUNS_DIR / "CURRENT"
        if ptr.exists():
            rid = ptr.read_text().strip()
            if (RUNS_DIR / rid / "state.json").exists():
                return cls.load(rid)
        runs = sorted(RUNS_DIR.glob("*/state.json"), key=lambda p: p.stat().st_mtime)
        if not runs:
            raise SystemExit("No runs yet. Start one with: kiln new ...")
        return cls.load(runs[-1].parent.name)


def _set_current(run_id: str) -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    (RUNS_DIR / "CURRENT").write_text(run_id)
