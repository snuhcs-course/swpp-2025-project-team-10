"""Data adapters for transforming external data to AI model entities."""

from .backend_adapter import BackendDataAdapter
from .frontend_adapter import FrontendDataAdapter

__all__ = ["BackendDataAdapter", "FrontendDataAdapter"]

