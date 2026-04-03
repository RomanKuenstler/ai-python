Step: Add visual understanding for image and document attachments, while keeping Qwen/Qwen3.5-4B as the text answer model

Work on the existing project and implement visual understanding for user attachments in a clean, stable way. Before changing code, inspect the current attachment flow, retriever pipeline, prompt builder, PDF/image handling, OCR pipeline, frontend attachment UX, and current model integration.

Objective

Extend the current attachment system so that image understanding becomes first-class for attached files, instead of relying only on OCR.

This step should improve attachment handling for:
	•	image files
	•	screenshots
	•	diagrams
	•	scanned pages
	•	visually rich PDFs
	•	visually relevant document attachments where OCR/text extraction alone is not enough

The final answer should still be produced by the normal text answer pipeline, but with better attachment-derived context created by a vision-capable model.

Explicit non-goals for this step

Do not implement:
	•	general video understanding
	•	image generation
	•	direct vision-based final answering in the frontend without text conversion
	•	automatic multimodal reranking unless it fits very cleanly
	•	replacing the main chat model with a vision model for all normal chat turns

Research requirements

Use official docs / official model cards / official library docs first to verify at minimum:
	1.	how Qwen/Qwen3.5-4B is intended to be used
	2.	what processor is required for image/document inputs
	3.	how image inputs and mixed image+text prompts should be formatted
	4.	what PDF/image preprocessing is recommended
	5.	how to safely structure the output of the vision step so it improves the downstream text answer step
	6.	any runtime, memory, and dependency implications

Required model strategy

1. Keep the current answer model

Continue using:
	•	hf.co/Qwen/Qwen3.5-4B

for:
	•	final user-facing answer generation
	•	assistant modes
	•	personalization
	•	GPT behavior
	•	normal text RAG flow

The model should be also used for:
	•	image understanding
	•	screenshot understanding
	•	visually rich PDF page understanding
	•	other image-like attachment understanding where useful

Architecture requirements

1. Introduce a visual attachment understanding step

Add a dedicated pre-answer attachment understanding stage to the attachment pipeline.

For visually relevant attachments:
	•	preprocess the attachment
	•	run OCR/text extraction where appropriate
	•	run visual understanding where appropriate
	•	produce a normalized structured text result
	•	feed that result into the existing attachment context flow

2. Hybrid attachment understanding

Do not replace OCR/text extraction.

For attachments, use a hybrid approach:
	•	OCR/text extraction remains available
	•	visual understanding is added when it provides value
	•	the final prompt gets structured text, not raw image blobs

3. Reuse existing architecture cleanly

Keep the code modular and reusable. Avoid duplicating logic across:
	•	image attachments
	•	PDF attachments
	•	future document-image attachment support

Scope of this step

Implement all of the following.

1. Image attachments with visual understanding

For attached image files such as:
	•	.png
	•	.jpg
	•	.jpeg
	•	.webp

the system must:
	•	continue to support OCR text extraction
	•	add visual understanding
	•	combine OCR-derived and visually derived information into a normalized attachment context
	•	send that attachment context into the retriever/prompt builder flow

2. PDF attachments with visual understanding where helpful

For attached PDFs:
	•	keep current text extraction behavior
	•	keep OCR fallback
	•	add a visual path for pages where visual understanding is useful
	•	allow page renders or selected page images to be processed by the vision model
	•	use the vision understanding especially when:
	•	the PDF is scanned
	•	diagrams are important
	•	layouts/tables/screenshots matter
	•	OCR/text extraction alone is weak

Do not over-engineer page region detection in this step. A page-level or simple-pass approach is enough.

3. Other attached documents where visual understanding may help

Review attachment handling for other supported document types and apply visual understanding only where it is clearly useful and stable.

For example:
	•	image-heavy PDF attachments
	•	screenshot-like HTML exports if applicable
	•	documents converted into images/pages for interpretation if that fits the current code cleanly

Do not force visual handling onto document types where text extraction is already clearly superior.

Required processing behavior

1. Attachment modality routing

Implement clean routing logic for attachments.

Examples:
	•	plain text attachment → text extraction only
	•	image attachment → OCR + vision understanding
	•	PDF attachment → text extraction + OCR fallback + optional page-level vision understanding
	•	EPUB attachment → usually text extraction only in this step unless a simple visual path fits naturally

2. Structured output from the vision step

The vision understanding should not just caption loosely. It should produce structured useful context for downstream answering.

For each visually processed attachment, generate a normalized text result that can include:
	•	a concise summary of what the image/document page contains
	•	important visible text if OCR misses or weakly extracts it
	•	important entities, labels, headings, sections, or diagram cues
	•	table/figure interpretation at a simple level where useful
	•	any useful warning if the content is low confidence or unclear

Design the prompt to the vision understanding so the output is practical for RAG/chat answering, not generic captioning fluff.

3. Downstream prompt integration

The final text answer model must receive the attachment-derived context as text.

The existing attachment context block should be extended to include:
	•	OCR-derived content
	•	visual-understanding-derived content
	•	source labels per attachment
	•	modality/type labels where helpful

Frontend requirements

1. Attachment UX stays familiar

Keep the current attachment UI structure stable.

Users should still be able to attach supported files, and the system should process them automatically.

2. Clear processing states

For visually processed attachments, the frontend should clearly handle:
	•	uploading
	•	analyzing
	•	processing
	•	failure

Do not leave users wondering whether the system is stuck.

Backend/API requirements

1. Attachment endpoints

Review and update the existing protected attachment/message APIs as needed so they support the new visual-understanding workflow.

2. Protected routes stay protected

All attachment-processing APIs must remain protected by authentication and existing authorization rules.

3. Typed response metadata

Return enough metadata so the frontend can handle:
	•	attachment processing status
	•	attachment type
	•	whether visual analysis was used
	•	error state if processing failed

Prompt-building requirements

1. Add visual-attachment context cleanly

Update the prompt builder so attachment context can include a new structured block for visually analyzed attachments.

2. Keep assistant modes intact

The following must still work:
	•	simple
	•	refine
	•	thinking

Visual attachment context must integrate cleanly into all relevant prompt paths.

3. Keep personalization / GPTs intact

Visual attachment understanding must not break:
	•	personalization
	•	GPT-specific instructions
	•	GPT-specific settings
	•	filtering
	•	user-specific settings

Dependency and runtime requirements

Update dependencies only as needed based on official usage.

Check and update where relevant:
	•	backend Python dependencies
	•	vision model runtime dependencies
	•	image processing dependencies
	•	PDF page rendering dependencies
	•	Dockerfiles
	•	compose files
	•	prod Dockerfiles
	•	prod compose
	•	docs

Validation requirements

This step is not complete when a vision model loads or a single image works.

It is complete only after the result has been checked, tested, and debugged where necessary.

Validate at minimum:
	1.	Qwen/Qwen3.5-4B still works correctly
	2.	image attachments are processed with visual understanding
	3.	OCR still works for image attachments
	4.	hybrid OCR + vision output is normalized correctly
	5.	PDF attachments still work
	6.	visually rich/scanned PDFs benefit from the visual path
	7.	attachment context is correctly inserted into the prompt
	8.	final answers improve for visual attachments
	9.	non-visual attachment flows are not broken
	10.	authentication protection remains intact
	11.	no regression from previous steps

If issues are found:
	1.	identify root cause
	2.	debug and fix
	3.	rerun validation
	4.	update docs and changelog

Testing requirements

Update and/or add tests where practical for:
	•	vision understanding wrapper loading
	•	image attachment routing
	•	OCR + vision hybrid attachment processing
	•	PDF visual attachment processing
	•	prompt builder integration for visual attachment context
	•	frontend processing states
	•	protected API behavior for attachment routes

Documentation requirements

Update at minimum:
	•	README.md
	•	docs/setup.md
	•	docs/development.md
	•	docs/production.md
	•	docs/testing.md
	•	docs/architecture.md
	•	docs/attachments.md
	•	docs/api.md
	•	changelog.md

Also document:
	•	which model remains the final answer model
	•	which model is used for visual attachment understanding
	•	supported attachment types
	•	when OCR is used
	•	when visual understanding is used
	•	known limitations

Deliverable expectations

When finished:
	•	the project supports visual understanding for image and visually relevant document attachments
	•	Qwen/Qwen3.5-4B remains the final text answer model
	•	image attachments work much better than OCR-only
	•	PDF attachments can benefit from visual understanding where helpful
	•	the implementation is clean and maintainable
	•	tests/docs/changelog are updated
	•	the result has been verified and debugged if needed