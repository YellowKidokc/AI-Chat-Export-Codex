from __future__ import annotations

from pathlib import Path

from .models import Conversation


class MarkdownWriter:
    """Persist conversations as Markdown documents."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, conversation: Conversation) -> Path:
        target = self.output_dir / f"{conversation.conversation_id}.md"
        target.write_text(conversation.to_markdown(), encoding="utf-8")
        return target
