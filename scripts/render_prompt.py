"""Prompt files live in /prompts as markdown with {{placeholders}}."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel

from config import PROMPTS_DIR

_PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


def to_text(value: Any) -> str:
    if isinstance(value, BaseModel):
        return value.model_dump_json(indent=2)
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False)
    return "" if value is None else str(value)


def render(name: str, **ctx: Any) -> str:
    text = (PROMPTS_DIR / f"{name}.md").read_text()
    missing = sorted({m for m in _PLACEHOLDER.findall(text) if m not in ctx})
    if missing:
        raise KeyError(f"prompts/{name}.md needs values for: {', '.join(missing)}")
    return _PLACEHOLDER.sub(lambda m: to_text(ctx[m.group(1)]), text)


def schema_text(model: type[BaseModel]) -> str:
    return json.dumps(model.model_json_schema(), indent=2)
