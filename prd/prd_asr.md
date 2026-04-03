Step: Add ASR / audio transcription with hf.co/Qwen/Qwen3-ASR-1.7B

Work on the existing project and implement audio transcription (ASR) end to end, using the official model card and official docs first. Do not guess APIs or runtime behavior. Before changing code, inspect the current codebase and current attachment / library / embedder / retriever / web UI flows, then verify the correct model usage from official sources.

Objective

Add audio transcription support using:
	•	ASR model: hf.co/Qwen/Qwen3-ASR-1.7B (this model should also be running inside Docker Model Runner in the compose.yml file)

This step must cover all three major flows:
	1.	Library audio uploads
Users can upload supported audio files into the library. These files must be transcribed first, then embedded and used like other knowledge files.
	2.	Audio attachments on user prompts
Users can attach supported audio files to a chat message. These files must be transcribed first, then continue through the existing attachment pipeline like normal attached files.
	3.	Microphone dictation for the user prompt
Users can record from their local device microphone in the web UI, send the recorded audio for transcription, receive the transcribed text back, and have that text inserted into the prompt input field for review/editing before sending the final message.

Research requirements

Use official docs / model cards / official library docs first to verify at minimum:
	1.	how Qwen/Qwen3-ASR-1.7B should be loaded and used for transcription
	2.	whether the model is intended for offline batch inference, streaming, or both in the libraries/runtimes we use
	3.	what processor/tokenizer/audio preprocessing is required
	4.	supported audio formats and recommended sample rates
	5.	whether resampling or mono conversion is recommended
	6.	required package versions
	7.	best official runtime path for our project architecture
	8.	any model-specific optimization guidance
	9.	how browser microphone recording should be done safely and compatibly for the web UI

Important constraints to respect
	•	Qwen/Qwen3-ASR-1.7B is an official Hugging Face ASR model and the model card describes it as supporting ASR and language identification for many languages/dialects. Implement it using the officially documented inference path for the libraries we actually use. (huggingface.co￼)
	•	browser microphone capture should use standard browser APIs such as navigator.mediaDevices.getUserMedia() and MediaRecorder, which are the documented browser mechanisms for requesting microphone input and recording it. (MDN￼) (MDN￼)

Supported audio input scope for this step

Support practical/common audio upload formats where feasible for the chosen stack. At minimum, implement a clearly documented allowed-extension list for audio transcription uploads and attachments. Choose the exact set based on what the runtime stack reliably supports after normalization/conversion.

Recommended target support includes common formats such as:
	•	.wav
	•	.mp3
	•	.m4a
	•	.mp4 audio track only if intentionally supported
	•	.webm
	•	.ogg

Do not silently accept unsupported formats. Validate clearly.

Architecture requirements

1. Introduce a dedicated ASR pipeline

Create a clean ASR/transcription pipeline instead of scattering transcription logic across the codebase.

The design should separate:
	•	audio file validation
	•	audio normalization/conversion
	•	model loading
	•	transcription inference
	•	text normalization/post-processing
	•	error handling
	•	metadata reporting

2. Prefer reusable service abstraction

Implement ASR in a reusable way so it can be used by:
	•	library ingestion
	•	message attachments
	•	microphone dictation

Do not duplicate transcription logic in three places.

3. Keep current architecture clean

The project already has:
	•	embedder pipeline
	•	retriever pipeline
	•	attachment flow
	•	library management
	•	web UI
	•	auth / multi-user
	•	GPTs / settings / filters / personalization

Integrate ASR into the current architecture cleanly.

Implementation requirements

1. Add model integration for Qwen/Qwen3-ASR-1.7B

Tasks:
	•	add config defaults for the ASR model
	•	implement model loading according to official usage
	•	implement processor/audio preprocessing correctly
	•	handle device/dtype config if needed
	•	avoid reloading the model unnecessarily
	•	add robust logging for load and inference failures

2. Add audio normalization / preprocessing

Before transcription, normalize audio into a model-friendly form.

This should include where needed:
	•	decode input audio
	•	convert sample rate as required by official guidance
	•	convert to mono if appropriate
	•	validate duration / size
	•	reject clearly broken files
	•	handle temporary files safely

Choose the exact implementation based on the official model/runtime requirements.

3. Library audio ingestion

Extend the library upload flow to support audio files.

Behavior:
	1.	user uploads supported audio file to library
	2.	backend stores file in the shared data/library flow
	3.	embedder or a dedicated ingestion service transcribes the audio first
	4.	resulting transcript becomes the content used for chunking and embedding
	5.	file metadata is persisted as normal
	6.	transcript-derived chunks are stored in Qdrant/Postgres like other knowledge files

Important:
	•	store metadata indicating the file was ingested via ASR
	•	keep ownership and permissions consistent with the current library rules
	•	keep user/global file enable/disable and tag behavior working

4. Audio attachments to chat prompts

Extend the attachment system to support audio files.

Behavior:
	1.	user attaches supported audio file to a prompt
	2.	backend transcribes it
	3.	transcription output is normalized
	4.	the result is inserted into the attachment-context flow
	5.	existing attachment behavior continues normally

Important:
	•	attached audio files must remain ephemeral
	•	they must not be permanently embedded in Qdrant
	•	they must not be permanently added to the library
	•	they should behave like the current temporary attachment pipeline

5. Decide and implement the cleanest processing ownership

Review the current architecture and choose the cleaner design:

Preferred design
Retriever submits temporary audio-transcription jobs to a reusable processing service that shares logic with the embedder pipeline.

This is preferred because:
	•	OCR / extraction / normalization patterns already exist
	•	temporary attachment processing should reuse existing ingestion quality standards
	•	future multimodal ingestion becomes easier

If a different design is cleaner in the actual codebase, use it, but keep a single reusable transcription pipeline.

6. Microphone dictation in the web UI

Add microphone dictation UX to the prompt composer.

Requirements:
	•	add a microphone button to the left of the send button
	•	the microphone button must have no background and no border
	•	when clicked:
	•	request microphone permission from the browser
	•	start recording from the local device microphone
	•	clearly show that dictation is listening
	•	while listening, show:
	•	Cancel button
	•	Finish button

Behavior:
	•	Cancel
	•	stops recording
	•	discards the recorded audio
	•	returns UI to normal prompt state
	•	Finish
	•	stops recording
	•	sends recorded audio to backend for transcription
	•	UI shows that transcription is in progress
	•	when transcription completes:
	•	the transcribed text is sent back to the frontend
	•	the prompt input field is filled with that text
	•	the user can still edit the text before clicking send

Important:
	•	do not auto-send the final chat message after dictation
	•	dictation only fills the input box
	•	the user remains in control of final submission

7. Web UI dictation states

Implement clean UI states for:
	•	idle
	•	requesting microphone permission
	•	listening/recording
	•	uploading/transcribing
	•	transcription success
	•	transcription failure

The UI should recover gracefully from:
	•	permission denied
	•	no microphone
	•	empty recording
	•	backend failure
	•	unsupported browser behavior

8. API requirements

Add protected authenticated APIs as needed for:
	•	audio library upload support
	•	audio attachment processing
	•	microphone dictation transcription endpoint

Design the endpoints cleanly. Likely needs:
	•	multipart/form-data for uploaded audio
	•	auth protection on all non-public routes
	•	consistent typed responses

For microphone dictation, a dedicated endpoint is acceptable if it keeps the frontend flow simple.

9. Metadata requirements

Persist or return useful metadata where appropriate, such as:
	•	source type = audio
	•	transcription method = asr
	•	model id used
	•	duration if available
	•	language if returned or detected and useful
	•	transcript quality flags if helpful

Do not overcomplicate this step, but design it cleanly.

10. Text normalization after transcription

After ASR, normalize transcript text before chunking or attachment injection.

At minimum consider:
	•	whitespace cleanup
	•	repeated blank line cleanup
	•	safe punctuation normalization if needed
	•	removal of obviously broken artifacts where reasonable

Do not over-edit transcripts aggressively.

File/library behavior requirements

Library uploads

Audio uploaded to the library should:
	•	follow current ownership rules
	•	respect existing admin/user permissions
	•	allow tagging like other library files if the current library flow supports tags
	•	become normal searchable knowledge after transcription and embedding

Attachments

Audio attachments should:
	•	follow current attachment limits and auth rules
	•	be processed temporarily
	•	be included in the prompt like other attachment-derived content

Config requirements

Add/update config as needed, for example:
	•	ASR model id
	•	allowed audio extensions
	•	max audio file size
	•	max audio duration if needed
	•	temp storage path
	•	sample rate config if required
	•	transcription timeout if needed

Do not add unnecessary config, but document everything introduced.

Dependency/runtime requirements

Update dependencies only as needed based on official guidance.

Check and update where relevant:
	•	backend Python dependencies
	•	audio decoding/conversion dependencies
	•	Dockerfiles
	•	compose files
	•	prod Dockerfiles
	•	prod compose
	•	docs

If ffmpeg or similar runtime support is needed, add it cleanly and document it.

Validation requirements

This step is not complete when the model loads or one happy path works.

It is complete only after the result has been checked, tested, and debugged where necessary.

Validate at minimum:
	1.	ASR model loads successfully
	2.	audio normalization works for supported formats
	3.	library audio upload works
	4.	uploaded library audio is transcribed and then embedded
	5.	retrieval can use transcript-derived knowledge
	6.	audio attachment to a prompt works
	7.	attached audio is transcribed and injected correctly
	8.	attached audio remains non-persistent
	9.	microphone dictation works end to end
	10.	microphone cancel works correctly
	11.	microphone finish + transcription fills the prompt input correctly
	12.	transcription errors are handled cleanly
	13.	auth-protected APIs remain protected
	14.	Step 1–13 functionality is not broken

If issues are found:
	1.	identify root cause
	2.	debug and fix
	3.	rerun validation
	4.	update docs and changelog

Testing requirements

Update and/or add tests where practical for:
	•	ASR model wrapper loading
	•	audio validation
	•	audio normalization/conversion
	•	transcription service behavior
	•	library audio ingestion
	•	attachment audio flow
	•	dictation endpoint
	•	frontend dictation state transitions
	•	permission denied / failure handling
	•	auth protection on transcription routes

Documentation requirements

Update at minimum:
	•	README.md
	•	docs/setup.md
	•	docs/development.md
	•	docs/production.md
	•	docs/testing.md
	•	docs/architecture.md
	•	docs/library.md
	•	docs/attachments.md
	•	changelog.md

Also document:
	•	supported audio file types
	•	required runtime dependencies such as ffmpeg if used
	•	how microphone dictation works
	•	any browser limitations
	•	any known ASR limitations

Deliverable expectations

When finished:
	•	the project supports ASR via hf.co/Qwen/Qwen3-ASR-1.7B
	•	library audio uploads work
	•	audio attachments work
	•	browser microphone dictation works
	•	the code is clean and reusable
	•	tests/docs/changelog are updated
	•	the result has been verified and debugged if needed
