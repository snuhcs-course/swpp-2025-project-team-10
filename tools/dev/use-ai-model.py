#!/usr/bin/env python3
"""Set VS Code interpreter to the ai-model virtualenv."""

from pathlib import Path

from set_interpreter import configure_interpreter


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    configure_interpreter(
        repo_root=repo_root,
        component="ai-model",
        interpreter_relpath="ai-model/.venv/bin/python",
        template_relpath=".vscode/settings.template.json",
        target_relpath=".vscode/settings.json",
        bootstrap_instructions=[
            "cd ai-model",
            "uv venv .venv",
            "uv sync",
        ],
    )


if __name__ == "__main__":
    main()
