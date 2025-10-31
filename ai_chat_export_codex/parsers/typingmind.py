from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from dateutil import parser as dateparser

from ..models import Conversation, ManifestSection, Message
from .base import ChatExportParser


class TypingMindParser(ChatExportParser):
    platform = "typingmind"

    def parse(self, section: ManifestSection) -> List[Conversation]:
        path = self._resolve_path(section)
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        if isinstance(data, dict):
            conversations_raw = data.get("conversations") or list(data.values())
        else:
            conversations_raw = data
        conversations: List[Conversation] = []
        for item in conversations_raw:
            convo_id = str(item.get("id") or item.get("conversationId") or item.get("title"))
            title = item.get("title") or convo_id
            created = self._parse_datetime(item.get("createdAt"))
            messages = []
            for message in item.get("messages", []):
                role = message.get("role") or message.get("from")
                content = message.get("content") or message.get("message") or ""
                timestamp = self._parse_datetime(message.get("createdAt") or message.get("timestamp"))
                attachments = message.get("attachments") or []
                messages.append(
                    Message(
                        role=role,
                        content=self._normalize_text(content),
                        timestamp=timestamp,
                        attachments=list(attachments),
                        metadata={k: str(v) for k, v in message.items() if k not in {"role", "from", "content", "message", "createdAt", "timestamp", "attachments"}},
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
                    metadata={k: str(v) for k, v in item.items() if k not in {"id", "conversationId", "title", "messages", "createdAt"}},
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
