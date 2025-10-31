from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class Message:
    role: str
    content: str
    timestamp: Optional[datetime] = None
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class Conversation:
    platform: str
    conversation_id: str
    title: str
    created_at: Optional[datetime]
    messages: List[Message]
    source_path: Path
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_markdown(self) -> str:
        lines: List[str] = []
        lines.append(f"# Conversation: {self.title}")
        if self.created_at:
            lines.append(f"Date: {self.created_at.isoformat()}")
        lines.append(f"Platform: {self.platform}")
        if self.metadata:
            lines.append("")
            lines.append("Metadata:")
            for key, value in self.metadata.items():
                lines.append(f"- {key}: {value}")
        lines.append("")
        for message in self.messages:
            header = f"## {message.role.capitalize()}"
            lines.append(header)
            if message.timestamp:
                lines.append(f"_{message.timestamp.isoformat()}_")
            lines.append(message.content.strip())
            if message.attachments:
                lines.append("")
                lines.append("Attachments:")
                for attachment in message.attachments:
                    lines.append(f"- {attachment}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"


@dataclass
class ManifestSection:
    platform: str
    source_name: str
    path: Path
    size_bytes: int
    conversation_ids: List[str]


@dataclass
class Manifest:
    sections: List[ManifestSection] = field(default_factory=list)

    def add_section(self, section: ManifestSection) -> None:
        self.sections.append(section)

    def to_dict(self) -> Dict[str, object]:
        return {
            "sections": [
                {
                    "platform": s.platform,
                    "source_name": s.source_name,
                    "path": str(s.path),
                    "size_bytes": s.size_bytes,
                    "conversation_ids": s.conversation_ids,
                }
                for s in self.sections
            ]
        }

    def iter_sections(self) -> List[ManifestSection]:
        return list(self.sections)
