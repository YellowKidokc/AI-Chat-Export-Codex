from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from dateutil import parser as dateparser

from ..models import Conversation, ManifestSection, Message
from .base import ChatExportParser


class ClaudeParser(ChatExportParser):
    platform = "claude"

    def parse(self, section: ManifestSection) -> List[Conversation]:
        path = self._resolve_path(section)
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            conversations_raw = data.get("conversations") or list(data.values())
        else:
            conversations_raw = data
        conversations: List[Conversation] = []
        for item in conversations_raw:
            convo_id = str(item.get("uuid") or item.get("id") or item.get("name"))
            title = item.get("name") or item.get("title") or convo_id
            created = self._parse_datetime(item.get("created_at") or item.get("date"))
            messages = []
            for message in item.get("messages", []):
                role = message.get("role") or message.get("type", "assistant")
                content = message.get("text") or message.get("content") or ""
                timestamp = self._parse_datetime(message.get("date") or message.get("timestamp"))
                messages.append(
                    Message(
                        role=role,
                        content=self._normalize_text(content),
                        timestamp=timestamp,
                        metadata={k: str(v) for k, v in message.items() if k not in {"role", "text", "content", "date", "timestamp"}},
                    )
                )
            conversations.append(
                Conversation(
                    platform=self.platform,
                    conversation_id=convo_id,
                    title=title,
                    created_at=created,
                    messages=messages,
                    source_path=path,
                    metadata={k: str(v) for k, v in item.items() if k not in {"uuid", "id", "name", "title", "messages", "created_at", "date"}},
                )
            )
        return conversations

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return dateparser.parse(value)
        except (ValueError, TypeError):
            return None
