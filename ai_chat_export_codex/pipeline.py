from __future__ import annotations

import json
from pathlib import Path
from typing import List

from rich.console import Console
from rich.progress import Progress

from .config import AppConfig
from .utils.file_manager import FileManager
from .parsers.registry import ParserRegistry
from .markdown import MarkdownWriter
from .rag.ingestor import RAGIngestor

console = Console()


class IngestionPipeline:
    """High level orchestration for the end-to-end workflow."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.file_manager = FileManager(config.max_section_size_mb)
        self.registry = ParserRegistry()
        self.markdown_writer = MarkdownWriter(config.output_dir)
        self.rag_ingestor = RAGIngestor(config.rag_config)

    def run(self) -> Path:
        self.config.ensure_directories()
        console.log("Preparing inputs…")
        manifest = self.file_manager.prepare(self.config.input_paths, self.config.workdir)
        self.config.manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
        console.log(f"Manifest written to {self.config.manifest_path}")

        sections = manifest.iter_sections()
        with Progress() as progress:
            task = progress.add_task("Parsing exports", total=len(sections))
            for section in sections:
                progress.update(task, description=f"Parsing {section.source_name}")
                parser = self.registry.get_parser(section.platform)
                conversations = parser.parse(section)
                for conversation in conversations:
                    markdown_path = self.markdown_writer.write(conversation)
                    self.rag_ingestor.add_conversation(markdown_path, conversation)
                progress.advance(task)

        console.log("Committing embeddings to vector store…")
        self.rag_ingestor.finalize()
        return self.config.manifest_path

    def preview(self, limit: int = 5) -> List[str]:
        """Return preview strings for the first N conversations."""
        manifest = self.file_manager.prepare(self.config.input_paths, self.config.workdir)
        previews: List[str] = []
        for section in manifest.iter_sections():
            parser = self.registry.get_parser(section.platform)
            conversations = parser.parse(section)
            for conv in conversations:
                previews.append(f"{conv.title} ({conv.platform}) -> {len(conv.messages)} messages")
                if len(previews) >= limit:
                    return previews
        return previews
