# Export Format Research

## Typing Mind
- **Format**: JSON export with top-level `conversations` array. Each conversation object contains `id`, `title`, `createdAt`, and a `messages` array.
- **Messages**: Each message includes `role` (user/assistant/system), `content`, optional `attachments`, and timestamps in ISO 8601 strings.
- **Notes**: Typing Mind bundles local files such as images alongside JSON in ZIP exports. Attachments are referenced by relative paths that should be preserved in metadata.

## Grok (XAI)
- **Format**: JSON export with `threads` array representing conversations. Each thread contains `id`, `title`, `created_at`, and `messages`.
- **Messages**: Each message includes `role`, `content`, optional `attachments`, and `created_at` timestamps. Some exports provide `author` instead of `role`.
- **Notes**: Multi-part answers may be delivered as multiple assistant messages; maintain chronological order.

## Google Gemini
- **Format**: JSON or HTML exports depending on the surface (web UI vs. mobile). JSON exports expose `conversations` with `conversationId`, `title`, `createdAt`, and `messages` arrays.
- **HTML**: Structured as alternating user/assistant `<div>` blocks that can be converted via HTML-to-Markdown utilities.
- **Notes**: Gemini includes metadata for the model used (e.g., `modelId`) and conversation locale; include these in metadata for filtering.

## Vector Database Recommendation
- **Primary**: [ChromaDB](https://www.trychroma.com/) for lightweight local deployment with persistent storage.
- **Alternatives**: Pinecone for managed hosting, Weaviate for hybrid cloud, or LanceDB for pure local setups.
- **Rationale**: ChromaDB offers simple installation, Python-native API, and suitability for development environments where self-hosting is preferred.

## Embedding Model Recommendation
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Reasoning**:
  - Balanced performance between quality and inference cost.
  - Works well on CPU-only environments.
  - Widely supported by vector databases and open-source tooling.
- **Chunking Strategy**: 800-token target chunks with 200-token overlap preserve context while enabling efficient retrieval.
