Below is a complete, production-grade prd.md tailored for Codex to implement Step 1 of your local RAG system.
It is structured so Codex can directly execute it as a spec, while still being readable and extensible for future steps.

⸻

📄 prd.md — Local RAG System (Step 1)

1. Overview

1.1 Goal

Build the first functional version (Step 1) of a local Retrieval-Augmented Generation (RAG) system using:
	•	Python (LangChain) → core logic (embedder + retriever)
	•	Qdrant → vector database
	•	PostgreSQL → persistent state + metadata + chat history
	•	Docker Compose → orchestration
	•	CLI interface → user interaction (initial phase only)

This step focuses on:
	•	File ingestion + embedding pipeline
	•	Retrieval + response generation
	•	Persistent tracking of data and chat history

⸻

2. High-Level Architecture

2.1 Services

Service	Description
embedder	Watches data/, processes files, generates embeddings, syncs with DB
retriever	CLI-based chat interface, performs similarity search + response generation
qdrant	Vector database
postgres	Persistent storage (metadata, hashes, chat history, retrieval logs)


⸻

3. Project Structure

.
├── compose.yml
├── README.md
├── changelog.md
├── prd
│   ├── prd_v1.md
│   ├── ...
├── docs/
│   ├── architecture.md
│   ├── embedder.md
│   ├── retriever.md
│   ├── database.md
│   └── setup.md
├── services/
│   ├── embedder/
│   │   ├── main.py
│   │   ├── watcher.py
│   │   ├── processor.py
│   │   ├── chunking.py
│   │   ├── embedding.py
│   │   ├── qdrant_client.py
│   │   ├── postgres_client.py
│   │   └── utils.py
│   ├── retriever/
│   │   ├── main.py
│   │   ├── retriever.py
│   │   ├── prompt_builder.py
│   │   ├── chat_history.py
│   │   ├── qdrant_client.py
│   │   ├── postgres_client.py
│   │   └── llm_client.py
├── data/
│   ├── tags.json
│   └── (user files)
├── prompts/
│   ├── guardrails.md
│   ├── assistant.md
│   └── ragcontext.md


⸻

4. Functional Requirements

⸻

4.1 Embedder Service

4.1.1 Responsibilities
	•	Monitor data/ directory
	•	Detect:
	•	New files
	•	Modified files
	•	Deleted files
	•	Process .txt and .md files only
	•	Generate embeddings
	•	Store in:
	•	Qdrant (vectors)
	•	PostgreSQL (metadata + state)

⸻

4.1.2 File Tracking Logic

Each file must be tracked using:
	•	File path
	•	SHA256 hash
	•	Last processed timestamp

Behavior:

Case	Action
New file	Embed + store
Changed file	Re-embed + update
Deleted file	Remove from Qdrant + Postgres


⸻

4.1.3 Tags System
	•	data/tags.json format:

{
  "file1.md": ["tag1", "tag2"],
  "notes.txt": ["projectA"]
}

	•	Tags must be:
	•	Loaded during processing
	•	Stored in PostgreSQL
	•	Attached as metadata in Qdrant

⸻

4.1.4 Text Processing Pipeline

Step 1: Normalization
	•	Remove extra whitespace
	•	Normalize line endings
	•	Strip invalid characters

Step 2: Semantic Chunking
	•	Markdown-aware splitting:
	•	Headers (#, ##, etc.)
	•	Paragraph blocks

Step 3: Token Chunking
	•	Max chunk size: 600
	•	Overlap: 100

⸻

4.1.5 Embedding
	•	Model: Gemma Embedding
	•	Each chunk → embedding vector

⸻

4.1.6 Qdrant Storage

Each vector must include metadata:

{
  "file_name": "...",
  "file_path": "...",
  "chunk_id": "...",
  "text": "...",
  "tags": [...],
  "hash": "...",
  "created_at": "...",
  "updated_at": "..."
}


⸻

4.1.7 PostgreSQL Storage

Tables:

files

id
file_path
file_name
hash
last_processed_at

chunks

id
file_id
chunk_id
text
tags


⸻

4.1.8 File Watcher
	•	Polling-based (initial version)
	•	Interval configurable (default: 10s)

⸻

4.2 Retriever Service

⸻

4.2.1 CLI Interface

User interaction:

> python main.py
You: What is X?
AI: ...


⸻

4.2.2 Retrieval Flow
	1.	User enters prompt
	2.	Embed query
	3.	Search Qdrant
	4.	Retrieve scored results
	5.	Filter results using a configurable minimum similarity score threshold
	6.	Sort remaining results by score descending
	7.	Take between the configured minimum and maximum number of results
	8.	Build the RAG context from the filtered results only

Retrieval score behavior
Each retrieved chunk must include a retrieval score returned by the vector database.

The retriever must support the following configuration:
	•	RETRIEVAL_SCORE_THRESHOLD
Minimum score required for a retrieved chunk to qualify as usable knowledge.
	•	RETRIEVAL_MIN_RESULTS
Minimum number of chunks to include if enough chunks pass the threshold.
	•	RETRIEVAL_MAX_RESULTS
Maximum number of chunks to include in the final RAG context.

Required retrieval rules
	•	Always retrieve scored candidates from Qdrant.
	•	Discard all candidates with score below RETRIEVAL_SCORE_THRESHOLD.
	•	Sort remaining candidates by score descending.
	•	Use at most RETRIEVAL_MAX_RESULTS.
	•	If fewer than RETRIEVAL_MIN_RESULTS pass the threshold, the retriever may proceed with fewer results.
	•	If no result passes the threshold, the retriever must continue without RAG knowledge and the model should answer accordingly.
	•	The score of every used chunk must be stored in PostgreSQL together with source metadata.

Important implementation note
The code must clearly document whether the returned value is:
	•	cosine similarity where higher is better, or
	•	distance where lower is better

For Step 1, normalize this into one internal field called score, where higher is always better, so the rest of the system can apply one consistent threshold rule.

⸻

4.2.3 Prompt Construction

Message structure:

SYSTEM:
[guardrails.md]

SYSTEM:
[assistant.md]

SYSTEM:
[ragcontext.md + retrieved knowledge]

SYSTEM:
[chat history]

USER:
[user prompt]


⸻

4.2.4 Retrieved Knowledge Injection

Include:
	•	Chunk text
	•	File source
	•	Tags

⸻

4.2.5 Chat History
	•	Stored in PostgreSQL

Table: chat_messages

id
session_id
role (user/assistant)
content
created_at


⸻

4.2.6 History Usage
	•	Configurable number of past messages (e.g., last 5 exchanges)

⸻

4.2.7 Response Storage

After each assistant response, store the retrieval evidence used for that answer.

retrieval_logs

id
assistant_message_id
user_message_id
session_id
source_file_name
source_file_path
chunk_id
chunk_text
retrieval_score
retrieved_at


Requirements
	•	Store only chunks actually used in the final RAG context.
	•	Store the exact retrieval score returned after internal normalization.
	•	This data must later support source display in a UI.

⸻

4.2.8 LLM
	•	Model: Qwen/Qwen3.5-4B
	•	Local inference via Docker model runner

⸻

5. Non-Functional Requirements

⸻

5.1 Code Quality
	•	Clean architecture
	•	Modular design
	•	Separation of concerns
	•	Type hints
	•	Docstrings
	•	Logging (structured)

⸻

5.2 Error Handling
	•	Graceful failures
	•	Retry mechanisms for DB/vector ops
	•	Clear logging

⸻

5.3 Performance
	•	Batch embedding support
	•	Efficient DB queries
	•	Avoid re-processing unchanged files

⸻

5.4 Extensibility

Design must allow future:
	•	UI integration (React)
	•	Multi-user sessions
	•	Advanced filtering (tags)
	•	Streaming responses

⸻

6. Docker Requirements

⸻

6.1 docker-compose Services
	•	embedder
	•	retriever
	•	qdrant
	•	postgres

⸻

6.2 Data Volume

Mount:

./data:/app/data


⸻

6.3 Environment Variables
	•	DB connection
	•	Qdrant URL
	•	Model endpoints
	•	Chunk size / overlap
	•	Similarity thresholds

⸻

7. Configuration

Create .env:

CHUNK_SIZE=600
CHUNK_OVERLAP=100

WATCH_INTERVAL=10

SCORE_THRESHOLD=0.70
MIN_RESULTS=2
MAX_RESULTS=8

HISTORY_LIMIT=5
LOG_LEVEL=INFO



Retrieval configuration meaning
	•	SCORE_THRESHOLD
Minimum acceptable similarity score for a chunk to be considered relevant knowledge.
	•	MIN_RESULTS
Preferred minimum number of chunks to include if enough relevant chunks are found.
	•	MAX_RESULTS
Hard upper limit for number of retrieved chunks inserted into the RAG context.

Example
If the retriever gets these scores:
	•	chunk A → 0.91
	•	chunk B → 0.84
	•	chunk C → 0.72
	•	chunk D → 0.61
and the config is:
SCORE_THRESHOLD=0.70
MIN_RESULTS=2
MAX_RESULTS=3

then the retriever uses:
	•	chunk A
	•	chunk B
	•	chunk C

and excludes chunk D.

⸻

8. Documentation Requirements

Codex MUST generate:

8.1 changelog.md
	•	Every change
	•	Timestamped

8.2 docs/

File	Content
architecture.md	System overview
embedder.md	Embedder details
retriever.md	Retrieval pipeline
database.md	Schema
setup.md	How to run


⸻

9. Development Guidelines
	•	Use LangChain
	•	Use Qdrant Python client
	•	Use psycopg2 or SQLAlchemy
	•	Follow PEP8
	•	Refactor continuously
	•	Avoid monolithic files

⸻

10. Future Considerations (Not in Step 1)
	•	React UI
	•	Auth system
	•	Tag-based filtering in retrieval
	•	Streaming responses
	•	Multi-modal inputs
	•	Advanced ranking (rerankers)

⸻

11. Acceptance Criteria

✅ Embedder:
	•	Detects new/changed/deleted files
	•	Stores embeddings in Qdrant
	•	Stores metadata in PostgreSQL

✅ Retriever:
Retriever acceptance criteria
	•	Accepts CLI input
	•	Retrieves scored vector matches from Qdrant
	•	Applies configurable score threshold
	•	Applies configurable min/max retrieved chunk limits
	•	Builds prompt with only accepted knowledge chunks
	•	Stores retrieval scores and source metadata in PostgreSQL
	•	Produces LLM response even when no chunk passes threshold

✅ Persistence:
	•	Chat history stored
	•	Retrieval logs stored

✅ System:
	•	Fully dockerized
	•	Clean codebase
	•	Documentation generated

⸻

12. Suggested Enhancements

Codex MAY optionally include:
	•	File size limits
	•	Logging levels (INFO/DEBUG)
	•	CLI flags (e.g., --reset-db)
	•	Health checks for services
	•   Use git commits 