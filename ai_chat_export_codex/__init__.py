"""AI Chat Export Codex package."""

from .config import AppConfig, RAGConfig

__all__ = ["AppConfig", "RAGConfig", "IngestionPipeline"]

try:  # pragma: no cover - optional dependency for lightweight imports
    from .pipeline import IngestionPipeline
except ModuleNotFoundError:  # pragma: no cover
    IngestionPipeline = None  # type: ignore
