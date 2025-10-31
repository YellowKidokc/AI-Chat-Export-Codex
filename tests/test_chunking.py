from pathlib import Path

from ai_chat_export_codex.config import RAGConfig
from ai_chat_export_codex.rag.ingestor import RAGIngestor
from ai_chat_export_codex.models import Conversation, Message


def test_chunk_text_respects_overlap(tmp_path: Path) -> None:
    text = " ".join([f"word{i}" for i in range(1000)])
    config = RAGConfig(chunk_size=100, chunk_overlap=20)
    ingestor = RAGIngestor(config)
    chunks = ingestor._chunk_text(text)
    assert all(len(chunk.split()) <= 100 for chunk in chunks)
    if len(chunks) > 1:
        first = chunks[0].split()
        second = chunks[1].split()
        assert first[-20:] == second[:20]


def test_pending_manifest_written_when_vector_store_missing(tmp_path: Path) -> None:
    config = RAGConfig(vector_store="none")
    ingestor = RAGIngestor(config)
    conversation = Conversation(
        platform="chatgpt",
        conversation_id="test",
        title="Test",
        created_at=None,
        messages=[Message(role="user", content="Hello")],
        source_path=tmp_path / "source.json",
    )
    markdown_path = tmp_path / "test.md"
    markdown_path.write_text("content", encoding="utf-8")
    ingestor.add_conversation(markdown_path, conversation)
    ingestor.finalize()
    manifest = Path("embeddings_manifest.json")
    assert manifest.exists()
    data = manifest.read_text(encoding="utf-8")
    assert "test" in data
    manifest.unlink()
