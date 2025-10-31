from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from dateutil import parser as dateparser

from ..models import Conversation, ManifestSection, Message
from .base import ChatExportParser


class ChatGPTParser(ChatExportParser):
    platform = "chatgpt"

    def parse(self, section: ManifestSection) -> List[Conversation]:
        path = self._resolve_path(section)
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            conversations_raw = data.get("conversations") or list(data.values())
        else:
            conversations_raw = data
        conversations: List[Conversation] = []
        for item in conversations_raw:
            if not item:
                continue
            convo_id = str(item.get("id") or item.get("conversation_id") or item.get("title"))
            title = item.get("title") or convo_id
            created = self._parse_datetime(item.get("create_time") or item.get("update_time"))
            messages = []
            mapping = item.get("mapping")
            if mapping:
                for key, node in mapping.items():
                    message = node.get("message")
                    if not message:
                        continue
                    author = message.get("author", {}).get("role", "assistant")
                    content_parts = message.get("content", {}).get("parts") or []
                    content = "\n\n".join(str(part) for part in content_parts)
                    created_at = self._parse_datetime(message.get("create_time"))
                    messages.append(
                        Message(
                            role=author,
                            content=self._normalize_text(content),
                            timestamp=created_at,
                            metadata={k: str(v) for k, v in message.items() if k not in {"author", "content", "create_time"}},
                        )
                    )
            else:
                for message in item.get("messages", []):
                    role = message.get("role")
                    content = message.get("content")
                    timestamp = self._parse_datetime(message.get("timestamp"))
                    messages.append(Message(role=role, content=self._normalize_text(content), timestamp=timestamp))
            conversations.append(
                Conversation(
                    platform=self.platform,
                    conversation_id=convo_id,
                    title=title,
                    created_at=created,
                    messages=messages,
                    source_path=path,
                    metadata={k: str(v) for k, v in item.items() if k not in {"id", "conversation_id", "title", "mapping", "messag", "create_time", "update_time"}},
                )
            )
        return conversations

    def _parse_datetime(self, value: str | float | None) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value))
        try:
            return dateparser.parse(str(value))
        except (ValueError, TypeError):
            return None
