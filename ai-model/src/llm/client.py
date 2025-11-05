"""LLM client supporting both OpenAI API and local models."""

import logging
import os
from dataclasses import dataclass
from typing import Any

from .config import LLMConfig

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A single message in a conversation."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ConversationTurn:
    """A turn in a two-LLM conversation."""

    speaker: str  # "recommender" or "critic"
    message: str
    reasoning: str | None = None


class LLMClient:
    """
    Unified LLM client supporting OpenAI API and local models.

    This client provides a consistent interface for both OpenAI API
    and local model inference, with automatic fallback.
    """

    def __init__(self, config: LLMConfig | None = None):
        """Initialize LLM client with configuration."""
        self.config = config or LLMConfig.from_env()
        self._setup_logging()

        if self.config.use_local_model:
            self._init_local_model()
        else:
            self._init_openai_client()

    def _setup_logging(self) -> None:
        """Configure logging."""
        if self.config.enable_logging:
            logging.basicConfig(
                level=getattr(logging, self.config.log_level),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )

    def _init_openai_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            if not self.config.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY not set in environment"
                )

            self.client = OpenAI(api_key=self.config.openai_api_key)
            self.model_type = "openai"
            logger.info(
                f"Initialized OpenAI client with model: "
                f"{self.config.openai_model}"
            )
        except ImportError:
            logger.warning(
                "OpenAI package not installed. "
                "Falling back to local model."
            )
            self.config.use_local_model = True
            self._init_local_model()

    def _init_local_model(self) -> None:
        """Initialize local model with transformers."""
        try:
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
            )
            import torch

            logger.info(
                f"Loading local model from: {self.config.local_model_path}"
            )

            # Determine best available device
            if torch.cuda.is_available():
                device = "cuda"
                torch_dtype = torch.float16
                device_map = "auto"
                logger.info("CUDA available - using GPU acceleration (float16)")
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"
                # MPS requires float32 for numerical stability
                torch_dtype = torch.float32
                device_map = None
                logger.info("MPS available - using Apple Silicon GPU acceleration")
            else:
                device = "cpu"
                torch_dtype = torch.float32
                device_map = None
                logger.info("Using CPU for inference (no GPU acceleration available)")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.local_model_path,
                trust_remote_code=True,
            )

            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model
            logger.info(f"Loading model with dtype={torch_dtype}, device={device}")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.local_model_path,
                torch_dtype=torch_dtype,
                device_map=device_map,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
            )

            # Move to device if device_map is not used
            if device_map is None:
                self.model = self.model.to(device)

            self.model.eval()
            self.device = device
            self.client = None  # Not using OpenAI client
            self.model_type = "local"

            logger.info(
                f"Successfully loaded local model: {self.config.local_model_name} on {device}"
            )

        except ImportError as e:
            logger.error(
                f"Failed to import transformers: {e}. "
                "Install with: pip install transformers torch"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            raise

    def generate(
        self,
        messages: list[Message],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate (overrides config)

        Returns:
            Generated text response
        """
        temp = temperature or self.config.temperature
        max_tok = max_tokens or self.config.max_tokens

        if self.config.enable_logging:
            logger.debug(
                f"Generating with {len(messages)} messages, "
                f"temp={temp}, max_tokens={max_tok}"
            )

        if self.model_type == "openai":
            return self._generate_openai(messages, temp, max_tok)
        else:
            return self._generate_local(messages, temp, max_tok)

    def _generate_openai(
        self, messages: list[Message], temperature: float, max_tokens: int
    ) -> str:
        """Generate using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=self.config.top_p,
            )
            content = response.choices[0].message.content
            if self.config.enable_logging:
                logger.debug(f"OpenAI response: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _generate_local(
        self, messages: list[Message], temperature: float, max_tokens: int
    ) -> str:
        """Generate using local model with transformers."""
        try:
            import torch

            # Format messages for the model
            # Gemma3 uses a specific chat template
            formatted_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Apply chat template
            prompt = self.tokenizer.apply_chat_template(
                formatted_messages,
                tokenize=False,
                add_generation_prompt=True,
            )

            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=2048,
            )

            # Move to same device as model
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate
            logger.debug(f"Generating with temperature={temperature}, max_tokens={max_tokens}")
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=self.config.top_p,
                    do_sample=temperature > 0,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

            # Decode only the generated part (skip input)
            generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]
            response = self.tokenizer.decode(
                generated_tokens,
                skip_special_tokens=True,
            )

            if self.config.enable_logging:
                logger.debug(f"Local model response: {response[:100]}...")

            return response.strip()

        except Exception as e:
            logger.error(f"Local model generation error: {e}")
            logger.exception("Full traceback:")
            # Fallback to a simple response
            logger.warning("Falling back to simple response due to error")
            return (
                "I apologize, but I encountered an error generating a response. "
                "Please try again."
            )

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float | None = None,
    ) -> str:
        """
        Simple chat interface with system prompt and user message.

        Args:
            system_prompt: System instruction for the LLM
            user_message: User's message
            temperature: Sampling temperature

        Returns:
            LLM response
        """
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_message),
        ]
        return self.generate(messages, temperature=temperature)

    def multi_turn_conversation(
        self,
        system_prompt: str,
        initial_message: str,
        max_turns: int = 3,
        temperature: float | None = None,
    ) -> list[Message]:
        """
        Generate a multi-turn conversation.

        Args:
            system_prompt: System instruction
            initial_message: Starting message
            max_turns: Maximum conversation turns
            temperature: Sampling temperature

        Returns:
            List of conversation messages
        """
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=initial_message),
        ]

        for turn in range(max_turns):
            response = self.generate(messages, temperature=temperature)
            messages.append(Message(role="assistant", content=response))

            if turn < max_turns - 1:
                # Generate follow-up (simplified)
                messages.append(
                    Message(
                        role="user",
                        content="Please continue your analysis.",
                    )
                )

        return messages

