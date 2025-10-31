from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from dateutil import parser as dateparser

from ..models import Conversation, ManifestSection, Message
from .base import ChatExportParser


class GeminiParser(ChatExportParser):
    platform = "gemini"

    def parse(self, section: ManifestSection) -> List[Conversation]:
        path = self._resolve_path(section)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".html":
            from markdownify import markdownify as md

            markdown = md(text)
            message_blocks = [block.strip() for block in markdown.split("\n\n") if block.strip()]
            messages = []
            for idx, block in enumerate(message_blocks):
                role = "assistant" if idx % 2 else "user"
                messages.append(Message(role=role, content=block))
            conversation = Conversation(
                platform=self.platform,
                conversation_id=path.stem,
                title=path.stem,
                created_at=None,
                messages=messages,
                source_path=path,
                metadata={"source_format": "html"},
            )
            return [conversation]

        data = json.loads(text)
        if isinstance(data, dict):
            conversations_raw = data.get("conversations") or list(data.values())
        else:
            conversations_raw = data
        conversations: List[Conversation] = []
        for convo in conversations_raw:
            convo_id = str(convo.get("id") or convo.get("conversationId") or convo.get("title"))
            title = convo.get("title") or convo_id
            created = self._parse_datetime(convo.get("createdAt"))
            messages = []
            for message in convo.get("messages", []):
                role = message.get("role") or message.get("author", "assistant")
                content = message.get("content") or message.get("text") or ""
                timestamp = self._parse_datetime(message.get("createTime") or message.get("timestamp"))
                messages.append(
                    Message(
                        role=role,
                        content=self._normalize_text(content),
                        timestamp=timestamp,
                        metadata={k: str(v) for k, v in message.items() if k not in {"role", "author", "content", "text", "createTime", "timestamp"}},
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
                    metadata={k: str(v) for k, v in convo.items() if k not in {"id", "conversationId", "title", "messages", "createdAt"}},
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
