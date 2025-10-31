from __future__ import annotations

from typing import Dict

from .base import ChatExportParser
from .claude import ClaudeParser
from .chatgpt import ChatGPTParser
from .typingmind import TypingMindParser
from .grok import GrokParser
from .gemini import GeminiParser
from .fallback import FallbackParser


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: Dict[str, ChatExportParser] = {
            "claude": ClaudeParser(),
            "chatgpt": ChatGPTParser(),
            "typingmind": TypingMindParser(),
            "grok": GrokParser(),
            "gemini": GeminiParser(),
            "unknown": FallbackParser(),
        }

    def get_parser(self, platform: str) -> ChatExportParser:
        return self._parsers.get(platform, self._parsers["unknown"])

    def get_default_parser(self) -> ChatExportParser:
        return self._parsers["unknown"]
