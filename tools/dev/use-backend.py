#!/usr/bin/env python3
"""Set VS Code interpreter to the backend virtualenv."""

from pathlib import Path

from set_interpreter import configure_interpreter


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    configure_interpreter(
        repo_root=repo_root,
        component="backend",
        interpreter_relpath="backend/.venv/bin/python",
        template_relpath=".vscode/settings.template.json",
        target_relpath=".vscode/settings.json",
        bootstrap_instructions=[
            "cd backend",
            "uv venv .venv",
            "uv sync --extra dev    # installs base deps plus the 'dev' extra (use --all-extras for everything)",
        ],
    )


if __name__ == "__main__":
    main()
