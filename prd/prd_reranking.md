Step: Add multimodal reranking with hf.co/Qwen/Qwen3-VL-Reranker-2B, served via Docker Model Runner in compose.yml

Work on the existing project and implement a second-stage reranking pipeline using:
	•	Reranker model: hf.co/Qwen/Qwen3-VL-Reranker-2B

This step must use official documentation first and must integrate the reranker through Docker Model Runner in compose.yml rather than ad-hoc local loading inside the application container.

Objective

Upgrade retrieval quality by adding a reranking stage after first-pass retrieval.

Current retrieval already uses:
	•	embeddings
	•	Qdrant vector search
	•	filtering
	•	multimodal sources
	•	OCR/text extraction
	•	visual assets
	•	source display in the UI

This step must improve final retrieval precision by:
	1.	retrieving a candidate pool from Qdrant
	2.	reranking those candidates with Qwen/Qwen3-VL-Reranker-2B
	3.	selecting the final top results from the reranked list
	4.	using those reranked results for:
	•	prompt context
	•	source display
	•	retrieval logging

Required model/runtime constraints

1. Use this exact reranker model

Use exactly:
	•	hf.co/Qwen/Qwen3-VL-Reranker-2B

Do not swap to another reranker model.

2. Serve it via Docker Model Runner

Run the reranker through Docker Model Runner using the Compose model integration.

This means:
	•	update compose.yml
	•	declare the reranker model in the Compose model configuration
	•	wire the service(s) to the Model Runner-provided endpoint
	•	do not rely on manually starting a separate one-off reranker process outside Compose

Docker’s official docs describe Compose support through the top-level models section, where Docker Model Runner can pull and run models and inject endpoint URLs into service containers. Docker also documents an OpenAI-compatible API surface for Model Runner.  ￼

Research requirements

Use official docs / model cards / official Docker docs first to verify at minimum:
	1.	how Qwen/Qwen3-VL-Reranker-2B is intended to be used
	2.	whether the reranker is text-only, image-aware, or multimodal in the exact usage path you implement
	3.	what runtime/API format is best supported in Docker Model Runner for this model
	4.	how to configure Docker Model Runner in Compose correctly
	5.	how your app should call the model runner endpoint from the backend service
	6.	what score/output shape the reranker returns
	7.	how to map the reranker score into the retrieval pipeline safely
	8.	any limitations relevant to your current source types

Important: do not guess the API shape. Verify the reranker’s documented usage and verify Docker Model Runner’s supported API format before wiring the integration.

Why this step exists

Embedding search is fast and good at broad recall, but it can still return candidates that are only loosely relevant. The reranker should provide a more precise second-pass score over the retrieved candidates so that the final context sent to the answer model is better.

This is especially important now that the system supports:
	•	text chunks
	•	OCR chunks
	•	multimodal/image-backed sources
	•	PDF page assets
	•	CSV-derived chunks
	•	file and tag filtering
	•	GPT-specific and user-specific config

Core implementation requirements

1. Add second-stage reranking

The retrieval pipeline must become:

query
→ first-pass embedding search in Qdrant
→ apply existing filters
→ rerank remaining top candidates with Qwen3-VL-Reranker-2B
→ sort by reranker score
→ select final top-k
→ build final RAG context

2. Keep first-pass retrieval

Do not replace Qdrant/vector retrieval.

Reranking must be a second stage, not the only retrieval stage.

3. Candidate pool design

Use first-pass retrieval to fetch a configurable candidate pool, for example top 20–50 candidates, then rerank that pool.

Do not try to rerank the whole corpus.

4. Support multimodal candidate types where cleanly supported

Your candidate abstraction should support at least:
	•	text chunks
	•	OCR text chunks
	•	CSV structured text chunks
	•	image/page-backed candidates where the reranker path supports them cleanly

If a certain multimodal candidate type is not yet stable in the first implementation, keep the system stable and document the limitation rather than forcing a brittle implementation.

5. Preserve existing filters

Reranking must happen after existing filtering rules are applied.

That includes:
	•	user global file enable/disable
	•	chat-specific file enable/disable
	•	user global tag filtering
	•	chat-specific tag filtering
	•	GPT-specific config when relevant

Docker Model Runner requirements

1. Update compose.yml

Modify compose.yml so the reranker model is declared and served via Docker Model Runner.

Use Docker’s official Compose model integration pattern.

2. Service wiring

Ensure the appropriate backend service gets the model endpoint through Compose / Model Runner integration and uses that endpoint for reranking.

3. Do not break existing model wiring

Keep current model integrations working:
	•	chat model
	•	embedding model
	•	any existing model-runner-based setup already in place

4. Document the setup

Update docs so it is clear:
	•	which model is served by Docker Model Runner
	•	how Compose wires the endpoint
	•	how the backend consumes it

Backend implementation requirements

1. Create a clean reranker abstraction

Implement a dedicated reranker service/module.

It should handle:
	•	model runner client calls
	•	candidate formatting
	•	reranker result parsing
	•	score normalization if needed
	•	error handling
	•	fallback behavior

2. Create a unified rerankable candidate representation

Candidates entering reranking should be represented in a consistent internal format, such as:
	•	candidate id
	•	candidate type
	•	file/source metadata
	•	text content if available
	•	image/asset reference if available
	•	original vector score
	•	tags / page number / title metadata

3. Preserve original vector score

Keep the original first-pass vector score in the pipeline and in logs.

4. Add reranker score

Add reranker score alongside the original vector score.

This is one of the “optional but nice” items and it should be included:
	•	store reranker score in retrieval logs
	•	include it in useful debug metadata
	•	optionally expose it in source metadata where appropriate

5. Final ranking

Use reranker score as the primary sort for final context selection once reranking is available.

If needed, keep original vector score available for diagnostics and future score fusion.

6. Fallback behavior

Include safe fallback behavior:
	•	if reranker is disabled → keep current retrieval behavior
	•	if reranker fails to load or call → log clearly and fall back to embedding-only retrieval
	•	if reranking of a given candidate type is unsupported in the first version → keep the pipeline stable and document the limitation

Retrieval pipeline requirements

1. New retrieval flow

Update the retrieval orchestration so it:
	•	retrieves candidate pool
	•	reranks the pool
	•	trims to final top-k after reranking
	•	uses reranked top-k for prompt building and source display

2. Final prompt context

The final prompt context must be built from the reranked results, not just the raw vector top-k.

3. Assistant mode compatibility

Reranking must work with:
	•	simple mode
	•	refine mode
	•	thinking mode

4. GPT compatibility

Reranking must work for:
	•	normal chats
	•	GPT chats
	•	GPT-specific settings and filters

Config requirements

Add/update config as needed, for example:
	•	RERANKER_ENABLED=true
	•	RERANKER_MODEL_ID=hf.co/Qwen/Qwen3-VL-Reranker-2B
	•	RERANKER_CANDIDATE_POOL=30
	•	RERANKER_FINAL_TOP_K=8
	•	RERANKER_TIMEOUT_SECONDS=...

Optional and recommended:
	•	RERANKER_MIN_SCORE=... if the score semantics support a stable threshold after verification

Do not add config blindly. Only add what is useful and document it clearly.

“Optional but nice” items to include in this step

Include these too:

1. Store both scores

Store:
	•	original vector score
	•	reranker score

2. Debug/source metadata support

Where it fits cleanly:
	•	log reranker score in retrieval debugging
	•	make reranker score available in source metadata or internal debugging output

3. Safe fallback

Implement a clean no-reranker fallback path if reranker is disabled or unavailable

Data model and logging requirements

Update persistence where needed so retrieval logs can store:
	•	original vector score
	•	reranker score
	•	final rank position
	•	candidate/source type if helpful

Keep schema changes clean and migration-backed.

Frontend requirements

No major UI redesign is required in this step.

But if source metadata already shows retrieval info, extend it cleanly where useful so reranker-related information can be surfaced for debugging or future display without breaking the current UI.

Do not overcomplicate the UI in this step.

Validation requirements

This step is not complete when the reranker model is merely declared in Compose.

It is complete only after the reranker is actually used in the retrieval path, validated, and debugged where necessary.

Validate at minimum:
	1.	hf.co/Qwen/Qwen3-VL-Reranker-2B is wired through Docker Model Runner in compose.yml
	2.	the reranker endpoint is reachable from the backend service
	3.	candidate pool retrieval still works
	4.	reranking executes on the candidate pool
	5.	final context selection uses reranked order
	6.	original vector score is still preserved
	7.	reranker score is stored/logged
	8.	fallback to embedding-only retrieval works when reranker is disabled or unavailable
	9.	filtering still works correctly before reranking
	10.	simple/refine/thinking modes still work
	11.	GPT chats still work
	12.	source display still works
	13.	no regression from previous steps

If issues are found:
	1.	identify root cause
	2.	debug and fix
	3.	rerun validation
	4.	update docs and changelog

Testing requirements

Update and/or add tests where practical for:
	•	reranker service/model runner client integration
	•	retrieval candidate pool → rerank → final top-k flow
	•	preservation of original vector score
	•	storage of reranker score
	•	fallback behavior when reranker is disabled/unavailable
	•	filtering before reranking
	•	compatibility with assistant modes
	•	compatibility with GPT and user-scoped settings

Documentation requirements

Update at minimum:
	•	README.md
	•	docs/setup.md
	•	docs/development.md
	•	docs/production.md
	•	docs/testing.md
	•	docs/architecture.md
	•	docs/api.md
	•	docs/retrieval.md or equivalent retrieval-specific doc
	•	changelog.md

Also document:
	•	that reranking is now a second-stage retrieval step
	•	that hf.co/Qwen/Qwen3-VL-Reranker-2B is used
	•	that it is served via Docker Model Runner in compose.yml
	•	candidate pool size / final top-k behavior
	•	fallback behavior
	•	score semantics and logging

Deliverable expectations

When finished:
	•	the project uses hf.co/Qwen/Qwen3-VL-Reranker-2B exactly
	•	the reranker is served through Docker Model Runner in compose.yml
	•	retrieval uses first-pass vector search plus second-pass reranking
	•	original vector score and reranker score are both preserved
	•	reranked results drive final prompt context selection
	•	fallback behavior is stable
	•	the implementation is clean and maintainable
	•	tests/docs/changelog are updated
	•	the result has been verified and debugged if needed