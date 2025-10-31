from __future__ import annotations

from pathlib import Path
from typing import List

from ..models import Conversation, ManifestSection, Message
from .base import ChatExportParser


class FallbackParser(ChatExportParser):
    platform = "unknown"

    def parse(self, section: ManifestSection) -> List[Conversation]:
        path = self._resolve_path(section)
        text = path.read_text(encoding="utf-8")
        message = Message(role="system", content=self._normalize_text(text))
        conversation = Conversation(
            platform=self.platform,
            conversation_id=path.stem,
            title=path.stem,
            created_at=None,
            messages=[message],
            source_path=path,
            metadata={"note": "Unrecognized format"},
        )
        return [conversation]
