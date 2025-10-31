# Architecture Overview

The AI Chat Export Codex implements a modular pipeline that transforms heterogeneous chat export formats into a Retrieval-Augmented Generation (RAG) knowledge base. The solution is organised into the following layers:

## 1. File Preparation
- **Module**: `ai_chat_export_codex.utils.file_manager`
- **Responsibilities**:
  - Accept files and zip archives from multiple AI platforms.
  - Extract archives into a working directory.
  - Detect oversize exports and split them into logical sub-sections capped at 25 MB.
  - Generate a manifest capturing the relationships between source files, generated sections, and conversation identifiers.

## 2. Parsing & Normalisation
- **Module**: `ai_chat_export_codex.parsers`
- **Responsibilities**:
  - Format detection is handled via the manifest and platform inference.
  - Platform-specific parsers (`ClaudeParser`, `ChatGPTParser`, `TypingMindParser`, `GrokParser`, `GeminiParser`) convert native structures into a shared `Conversation` model.
  - A fallback parser serialises unknown formats as raw markdown to guarantee forward progress.

## 3. Markdown Conversion
- **Module**: `ai_chat_export_codex.markdown`
- **Responsibilities**:
  - Persist each parsed conversation to a well-structured Markdown file using a consistent template.
  - Preserve metadata such as timestamps, attachments, and platform identifiers in a human-readable layout.

## 4. RAG Ingestion
- **Module**: `ai_chat_export_codex.rag.ingestor`
- **Responsibilities**:
  - Convert Markdown documents into embeddings with configurable chunk size and overlap.
  - Persist embeddings into a vector store (ChromaDB by default) or emit a manifest when vector infrastructure is unavailable.
  - Capture metadata (platform, conversation ID, custom fields) to enable filtered semantic search.

## 5. Command-Line Interface
- **Module**: `ai_chat_export_codex.cli`
- **Responsibilities**:
  - Provide `run` and `preview` commands for end-to-end ingestion or quick validation.
  - Manage working directories, progress output, and user feedback.

## Extensibility
- Parsers follow a pluggable registry pattern to simplify the addition of new platforms.
- Configuration objects (`AppConfig`, `RAGConfig`) encapsulate tunable parameters such as chunk sizing, vector backends, and output paths.
- Optional dependencies allow deployments without GPU/vector capabilities; the pipeline still emits actionable manifests for deferred embedding.
