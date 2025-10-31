from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, List

from ..models import Conversation, ManifestSection


class ChatExportParser(ABC):
    platform: str

    @abstractmethod
    def parse(self, section: ManifestSection) -> List[Conversation]:
        ...

    def _resolve_path(self, section: ManifestSection) -> Path:
        return section.path

    def _normalize_text(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")
