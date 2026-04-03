Step: Update models to hf.co/Qwen/Qwen3.5-4B and hf.co/Qwen/Qwen3-VL-Embedding-2B

Work on the existing project and implement this model upgrade carefully, using official model cards and official documentation first. Do not guess APIs or model behavior. Before making code changes, inspect the current codebase and current model integration points, then verify the correct usage patterns from the official sources.

Objective

Update the project to use:
	•	Chat model: hf.co/Qwen/Qwen3.5-4B
	•	Embedding model: hf.co/Qwen/Qwen3-VL-Embedding-2B

Then adjust the code, config, startup flow, dependencies, and docs so the system works correctly and efficiently with these models.

Research requirements

Use official docs / model cards / official library docs to verify at minimum:
	1.	how Qwen/Qwen3.5-4B should be loaded and used for chat/instruction generation
	2.	how Qwen/Qwen3-VL-Embedding-2B should be loaded and used for embeddings
	3.	whether the embedding model supports:
	•	text-only inputs
	•	image inputs
	•	mixed multimodal inputs
	4.	recommended inference libraries / runtimes
	5.	required package versions
	6.	any tokenizer / processor requirements
	7.	any prompt formatting or message-formatting requirements
	8.	any model-specific optimization guidance
	9.	any constraints that affect our current architecture

Do not assume the existing model wrapper is still correct after the upgrade.

Important model constraints to respect
	•	Qwen/Qwen3.5-4B is a post-trained Hugging Face Transformers-format model compatible with common runtimes like Transformers and vLLM, but the exact implementation in this repo must match the officially documented loading/inference pattern for the libraries we are actually using.  ￼
	•	Qwen/Qwen3-VL-Embedding-2B is a multimodal embedding model, intended for embedding inputs such as text, images, screenshots, and videos into a shared representation space. It is not just a plain text embedding model, so update the embedding integration accordingly and do not treat it as a generic sentence-transformer without verification.  ￼

Implementation requirements

1. Inspect and update model integration

Find all current model-related code paths, including:
	•	chat model loading
	•	chat inference wrappers
	•	embedding model loading
	•	embedding generation
	•	OCR / image / attachment integration where relevant
	•	config/env handling
	•	Docker / compose / prod compose
	•	docs

Then update them for the new models.

2. Chat model update

Replace the current chat model configuration with hf.co/Qwen/Qwen3.5-4B.

Tasks:
	•	update config defaults
	•	update model-loading code
	•	update tokenizer / processor handling if needed
	•	update prompt/message formatting if required by official docs
	•	ensure assistant modes still work:
	•	simple
	•	refine
	•	thinking
	•	ensure personalization, GPT instructions, filters, and attachments still flow into the prompt correctly

3. Embedding model update

Replace the current embedding model configuration with hf.co/Qwen/Qwen3-VL-Embedding-2B.

Tasks:
	•	update embedding service configuration
	•	update embedding wrapper to the officially recommended API usage
	•	verify whether embeddings must use a processor instead of a simple tokenizer-only path
	•	verify whether instruction/query/document prefixes are recommended and implement them if officially supported
	•	make the implementation robust for current text ingestion
	•	prepare the abstraction so image embeddings can be added cleanly later without another large refactor

4. Preserve current functionality

The project already supports:
	•	text / markdown / html / pdf / epub ingestion
	•	retrieval
	•	web UI chat
	•	assistant modes
	•	personalization
	•	GPTs
	•	filtering
	•	auth / multi-user / library management

This upgrade must not break existing functionality.

5. Optimization and cleanup

While updating the models, improve the implementation where useful:
	•	remove outdated model-specific hacks
	•	cleanly separate model wrappers from business logic
	•	centralize model config
	•	improve error handling
	•	improve logging around model load/inference failures
	•	avoid duplicate model-loading logic
	•	add model capability comments/docstrings where helpful

6. Runtime and dependency updates

Update dependencies as needed based on official guidance.

Check and update:
	•	Python dependencies
	•	Dockerfiles
	•	compose files
	•	prod Dockerfiles
	•	prod compose
	•	environment variables
	•	startup scripts

Do not upgrade unrelated packages without reason.

7. Config updates

Update the project’s config/env layer so the new model names are the defaults.

Add or update only what is needed, for example:
	•	chat model id
	•	embedding model id
	•	model device / dtype config if applicable
	•	batch size / max tokens / embedding dimension handling if needed
	•	any processor-specific config

8. LangChain compatibility

We are using LangChain in the project. Ensure the integration remains correct.

If the best official usage for these models is not a direct LangChain wrapper, implement a clean internal adapter so the rest of the app can still use the existing architecture cleanly.

Do not force a bad LangChain abstraction if a thin internal wrapper is more correct.

9. Embedding pipeline considerations

Because the new embedding model is multimodal, review the current embedding pipeline and ensure:
	•	text extraction still produces the correct text inputs
	•	current file processors still feed embeddings correctly
	•	metadata/chunking remains unchanged unless needed
	•	future image-embedding support can be added cleanly

10. Attachments compatibility

Review the temporary attachment-processing flow too. If attachments currently use embedding-related code paths or shared processing abstractions, make sure the new model integration does not break them.

Validation requirements

This step is not complete when the model IDs are merely changed.

It is complete only after implementation has been checked, tested, and debugged where necessary.

Validate at minimum:
	1.	chat model loads successfully
	2.	embedding model loads successfully
	3.	text embedding still works for current knowledge ingestion
	4.	new files can still be embedded
	5.	retrieval still returns results
	6.	chat still works end-to-end
	7.	all assistant modes still work
	8.	personalization still works
	9.	GPT chats still work
	10.	attachments still work
	11.	auth-protected app still works
	12.	dev setup still works
	13.	prod-oriented setup still works
	14.	no regression from previous steps

If issues are found:
	1.	identify root cause
	2.	debug and fix
	3.	rerun validation
	4.	update docs and changelog

Testing requirements

Update and/or add tests where practical for:
	•	model wrapper loading
	•	embedding generation
	•	retrieval pipeline compatibility
	•	assistant mode compatibility
	•	prompt builder compatibility
	•	config loading
	•	startup failure handling for missing/invalid model config

Documentation requirements

Update at minimum:
	•	README.md
	•	docs/setup.md
	•	docs/development.md
	•	docs/production.md
	•	docs/testing.md
	•	docs/architecture.md
	•	changelog.md

Also document:
	•	the new chat model
	•	the new embedding model
	•	any runtime requirements
	•	any special loading behavior
	•	any known limitations

Deliverable expectations

When finished:
	•	the codebase should be updated cleanly
	•	the new models should be the defaults
	•	the system should run correctly with them
	•	the implementation should follow official usage guidance
	•	tests/docs/changelog should be updated
	•	the result should be verified and debugged if needed