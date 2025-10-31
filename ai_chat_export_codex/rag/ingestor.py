from __future__ import annotations

import json
from pathlib import Path
from typing import List

try:
    import chromadb
except Exception:  # pragma: no cover - optional dependency
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None  # type: ignore

from ..config import RAGConfig
from ..models import Conversation


class RAGIngestor:
    """Push processed conversations into a vector store."""

    def __init__(self, config: RAGConfig) -> None:
        self.config = config
        self.pending: List[tuple[Path, Conversation]] = []
        self._client = None
        self._collection = None
        self._embedder = None
        if chromadb and config.vector_store == "chromadb":
            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection("ai_chat_export_codex")
        if SentenceTransformer:
            self._embedder = SentenceTransformer(config.embedding_model)

    def add_conversation(self, markdown_path: Path, conversation: Conversation) -> None:
        self.pending.append((markdown_path, conversation))

    def finalize(self) -> None:
        if not self.pending:
            return
        if not self._collection or not self._embedder:
            self._write_embeddings_manifest()
            return
        documents = []
        metadatas = []
        ids = []
        for path, conversation in self.pending:
            content = path.read_text(encoding="utf-8")
            for idx, chunk in enumerate(self._chunk_text(content)):
                documents.append(chunk)
                metadatas.append(
                    {
                        "platform": conversation.platform,
                        "conversation_id": conversation.conversation_id,
                        "source_path": str(path),
                        **conversation.metadata,
                    }
                )
                ids.append(f"{conversation.conversation_id}-{idx}")
        embeddings = self._embedder.encode(documents, show_progress_bar=False)  # type: ignore[operator]
        self._collection.add(documents=documents, metadatas=metadatas, ids=ids, embeddings=embeddings)
        self.pending.clear()

    def _chunk_text(self, text: str) -> List[str]:
        size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        words = text.split()
        chunks: List[str] = []
        start = 0
        while start < len(words):
            end = min(len(words), start + size)
            chunks.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start = max(end - overlap, start + 1)
        return chunks

    def _write_embeddings_manifest(self) -> None:
        manifest_path = Path("embeddings_manifest.json")
        payload = []
        for path, conversation in self.pending:
            payload.append(
                {
                    "markdown_path": str(path),
                    "platform": conversation.platform,
                    "conversation_id": conversation.conversation_id,
                    "metadata": conversation.metadata,
                }
            )
        manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.pending.clear()
