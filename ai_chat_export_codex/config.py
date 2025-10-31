from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class RAGConfig:
    """Configuration for the retrieval layer."""

    vector_store: str = "chromadb"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 800
    chunk_overlap: int = 200
    metadata_fields: List[str] = field(default_factory=lambda: ["platform", "conversation_id", "date"])


@dataclass
class AppConfig:
    """Top-level configuration for the pipeline."""

    input_paths: List[Path]
    workdir: Path
    output_dir: Path
    manifest_path: Optional[Path] = None
    rag_config: RAGConfig = field(default_factory=RAGConfig)
    max_section_size_mb: int = 25

    def ensure_directories(self) -> None:
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.manifest_path is None:
            self.manifest_path = self.workdir / "manifest.json"
