"""Configuration for LLM clients."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class LLMConfig:
    """Configuration for LLM client."""

    # Model selection
    use_local_model: bool = True
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # Local model settings
    local_model_path: str | None = None
    local_model_name: str = "gemma3-4b-it"
    local_model_device: Literal["cpu", "cuda", "mps"] = "cpu"

    # Generation parameters
    temperature: float = 0.7
    max_tokens: int = 200  # DM-style responses with reasoning (2-3 sentences)
    top_p: float = 0.9

    # Logging
    enable_logging: bool = True
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load configuration from environment variables."""
        use_local = os.getenv("USE_LOCAL_MODEL", "true").lower() == "true"

        # Resolve local model path
        local_path = os.getenv("LOCAL_MODEL_PATH", "../gemma3-4b-it")
        if local_path and not Path(local_path).is_absolute():
            # Make relative to ai-model directory
            base_dir = Path(__file__).parent.parent.parent.parent
            local_path = str(base_dir / local_path)

        return cls(
            use_local_model=use_local,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            local_model_path=local_path,
            local_model_name=os.getenv(
                "LOCAL_MODEL_NAME", "gemma3-4b-it"
            ),
            local_model_device=os.getenv("LOCAL_MODEL_DEVICE", "cpu"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            enable_logging=os.getenv(
                "ENABLE_LLM_LOGGING", "true"
            ).lower()
            == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

