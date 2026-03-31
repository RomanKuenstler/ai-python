# OCR

## Runtime Support

The embedder image installs OCR dependencies so Step 2 can run inside Docker:

- `tesseract-ocr`
- `tesseract-ocr-eng`
- `poppler-utils`

## Config

- `ENABLE_OCR=true` enables OCR in the processor.
- `PDF_OCR_MODE` supports `off`, `fallback`, and `ocr_only`.
- `OCR_LANGUAGE` sets the Tesseract language.
- `OCR_ENABLE_PREPROCESSING` is the master preprocessing switch.
- `OCR_PREPROCESS_GRAYSCALE`, `OCR_PREPROCESS_THRESHOLD`, `OCR_PREPROCESS_DENOISE`, and `OCR_PREPROCESS_CONTRAST` tune preprocessing.

## Validation Notes

- The local host used during development did not have `tesseract` installed, so OCR was validated at the code and container-runtime level rather than with a host-native OCR smoke run.
- The Docker image is the intended runtime for full OCR support.
