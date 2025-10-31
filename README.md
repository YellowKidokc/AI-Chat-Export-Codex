# AI-Chat-Export-Codex

AI-Chat-Export-Codex ingests heterogeneous chat exports (Claude, ChatGPT, Typing Mind, Grok, Gemini) and prepares a Retrieval-Augmented Generation (RAG) workspace. The project standardises formats, generates Markdown archives, and optionally embeds conversations into a vector database.

## Features
- Automatic extraction of ZIP archives and large file splitting capped at 25 MB.
- Platform-aware parsers that convert native exports into a unified conversation model.
- Markdown conversion preserving role, timestamps, and attachments.
- Pluggable RAG ingestion layer using ChromaDB (with fallbacks when unavailable).
- Typer-based CLI with progress reporting and preview capabilities.

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[vector]
```

The `[vector]` extra installs ChromaDB and SentenceTransformers for embedding generation. If you skip the extra, the pipeline will emit an `embeddings_manifest.json` file describing conversations to embed later.

## Usage
Run the full ingestion pipeline:
```bash
aicec run path/to/export.zip another/export.json --workdir .aicec/workdir --output .aicec/markdown
```

Preview the first few parsed conversations without writing Markdown:
```bash
aicec preview path/to/export.zip --limit 3
```

## Project Structure
- `ai_chat_export_codex/config.py` – Configuration dataclasses.
- `ai_chat_export_codex/utils/file_manager.py` – Extraction, size checks, and manifest generation.
- `ai_chat_export_codex/parsers/` – Platform-specific parsers and fallback implementation.
- `ai_chat_export_codex/markdown.py` – Markdown writer utilities.
- `ai_chat_export_codex/rag/ingestor.py` – Embedding and vector store integration.
- `ai_chat_export_codex/cli.py` – Command-line entry points.

## Documentation
Additional documentation can be found in the `docs/` directory:
- `docs/architecture.md` – High-level system overview.
- `docs/format-research.md` – Research notes on export formats, vector stores, and embedding strategy.

## Testing
```bash
pytest
```

(Tests currently focus on ensuring manifest and parser stability; extend as the project evolves.)
