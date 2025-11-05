#!/usr/bin/env python3
"""Shared utilities for configuring VS Code interpreter settings."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable


def _strip_comments(source: str) -> str:
    """Remove // and /* */ comments so JSON parsing succeeds."""
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    source = re.sub(r"//.*", "", source)
    return source


def _load_json(path: Path, *, allow_missing: bool = True) -> dict:
    if not path.exists():
        if allow_missing:
            return {}
        raise FileNotFoundError(path)

    text = path.read_text(encoding="utf-8")
    cleaned = _strip_comments(text).strip()
    if not cleaned:
        return {}

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc


def configure_interpreter(
    *,
    repo_root: Path,
    component: str,
    interpreter_relpath: str,
    template_relpath: str,
    target_relpath: str,
    bootstrap_instructions: Iterable[str],
) -> None:
    repo_root = repo_root.resolve()
    interpreter_path = (repo_root / interpreter_relpath)
    template_path = (repo_root / template_relpath).resolve()
    target_path = (repo_root / target_relpath).resolve()

    if not interpreter_path.exists() or not os.access(interpreter_path, os.X_OK):
        rel = interpreter_path.relative_to(repo_root)
        print(f"Expected {component} virtualenv at {rel} (missing or lacks python).", file=sys.stderr)
        if bootstrap_instructions:
            print("Bootstrap it, for example:", file=sys.stderr)
            for line in bootstrap_instructions:
                print(f"  {line}", file=sys.stderr)
        sys.exit(1)

    interpreter_abs = interpreter_path.absolute()

    try:
        template_data = _load_json(template_path, allow_missing=False)
    except (FileNotFoundError, ValueError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    try:
        current_data = _load_json(target_path, allow_missing=True)
    except ValueError as exc:
        print(f"Refusing to overwrite malformed {target_path.relative_to(repo_root)}: {exc}", file=sys.stderr)
        sys.exit(1)

    merged = {**template_data, **current_data}
    merged["python.defaultInterpreterPath"] = str(interpreter_abs)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as fh:
        json.dump(merged, fh, indent=2)
        fh.write("\n")

    rel_target = target_path.relative_to(repo_root)
    print(f"Set VS Code interpreter to {interpreter_path} (written to {rel_target})")


__all__ = ["configure_interpreter"]
