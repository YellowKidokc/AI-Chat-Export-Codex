from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from dateutil import parser as dateparser

from ..models import Conversation, ManifestSection, Message
from .base import ChatExportParser


class GrokParser(ChatExportParser):
    platform = "grok"

    def parse(self, section: ManifestSection) -> List[Conversation]:
        path = self._resolve_path(section)
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            conversations_raw = data.get("threads") or list(data.values())
        else:
            conversations_raw = data
        conversations: List[Conversation] = []
        for thread in conversations_raw:
            convo_id = str(thread.get("id") or thread.get("thread_id"))
            title = thread.get("title") or f"Grok Conversation {convo_id}"
            created = self._parse_datetime(thread.get("created_at"))
            messages = []
            for message in thread.get("messages", []):
                role = message.get("role") or message.get("author", "assistant")
                content = message.get("content") or message.get("text") or ""
                timestamp = self._parse_datetime(message.get("created_at") or message.get("timestamp"))
                attachments = message.get("attachments") or []
                messages.append(
                    Message(
                        role=role,
                        content=self._normalize_text(content),
                        timestamp=timestamp,
                        attachments=list(attachments),
                        metadata={k: str(v) for k, v in message.items() if k not in {"role", "author", "content", "text", "created_at", "timestamp", "attachments"}},
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
                    metadata={k: str(v) for k, v in thread.items() if k not in {"id", "thread_id", "title", "messages", "created_at"}},
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
