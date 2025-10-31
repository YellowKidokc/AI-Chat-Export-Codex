from __future__ import annotations

import json
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from ..models import Manifest, ManifestSection


@dataclass
class FileManager:
    max_section_size_mb: int

    def prepare(self, input_paths: Iterable[Path], workdir: Path) -> Manifest:
        workdir.mkdir(parents=True, exist_ok=True)
        manifest = Manifest()
        for input_path in input_paths:
            if input_path.suffix == ".zip":
                extracted_paths = self._extract_zip(input_path, workdir)
            else:
                extracted_paths = [self._copy_input(input_path, workdir)]
            for path in extracted_paths:
                sections = self._split_if_needed(path)
                manifest.sections.extend(sections)
        return manifest

    def _extract_zip(self, zip_path: Path, workdir: Path) -> List[Path]:
        target_dir = workdir / zip_path.stem
        if target_dir.exists():
            shutil.rmtree(target_dir)
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(target_dir)
        return [p for p in target_dir.rglob("*") if p.is_file()]

    def _copy_input(self, path: Path, workdir: Path) -> Path:
        target = workdir / path.name
        if path.resolve() != target.resolve():
            shutil.copy2(path, target)
        return target

    def _split_if_needed(self, path: Path) -> List[ManifestSection]:
        size_bytes = path.stat().st_size
        max_bytes = self.max_section_size_mb * 1024 * 1024
        if size_bytes <= max_bytes:
            conversations = self._load_conversations(path)
            conversation_ids = list(conversations.keys()) if isinstance(conversations, dict) else []
            return [
                ManifestSection(
                    platform=self._infer_platform(path),
                    source_name=path.name,
                    path=path,
                    size_bytes=size_bytes,
                    conversation_ids=conversation_ids,
                )
            ]

        sections: List[ManifestSection] = []
        conversations = self._load_conversations(path)
        current_batch: List[str] = []
        current_size = 0
        batch_index = 0
        for convo_id, convo_data in conversations.items():
            encoded = json.dumps(convo_data).encode("utf-8")
            prospective_size = current_size + len(encoded)
            if prospective_size > max_bytes and current_batch:
                section_path = self._write_batch(path, batch_index, current_batch, conversations)
                sections.append(
                    ManifestSection(
                        platform=self._infer_platform(path),
                        source_name=f"{path.name}::part{batch_index}",
                        path=section_path,
                        size_bytes=section_path.stat().st_size,
                        conversation_ids=list(current_batch),
                    )
                )
                batch_index += 1
                current_batch = []
                current_size = 0
            current_batch.append(convo_id)
            current_size += len(encoded)
        if current_batch:
            section_path = self._write_batch(path, batch_index, current_batch, conversations)
            sections.append(
                ManifestSection(
                    platform=self._infer_platform(path),
                    source_name=f"{path.name}::part{batch_index}",
                    path=section_path,
                    size_bytes=section_path.stat().st_size,
                    conversation_ids=list(current_batch),
                )
            )
        return sections

    def _write_batch(self, source: Path, index: int, ids: List[str], conversations: dict) -> Path:
        target = source.with_name(f"{source.stem}_part{index}{source.suffix}")
        payload = {convo_id: conversations[convo_id] for convo_id in ids}
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def _load_conversations(self, path: Path) -> dict:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return {str(i): item for i, item in enumerate(data)}
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        return {"full": path.read_text(encoding="utf-8")}

    def _infer_platform(self, path: Path) -> str:
        name = path.name.lower()
        if "claude" in name or "anthropic" in name:
            return "claude"
        if "chatgpt" in name or "openai" in name:
            return "chatgpt"
        if "typing" in name:
            return "typingmind"
        if "grok" in name:
            return "grok"
        if "gemini" in name or "bard" in name:
            return "gemini"
        return "unknown"
