from __future__ import annotations

from io import BytesIO

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from services.common.config import Settings
from services.embedder.processors.shared_normalization import normalize_block_text


def preprocess_image(image: Image.Image, settings: Settings) -> Image.Image:
    if not settings.ocr_enable_preprocessing:
        return image
    processed = image
    if settings.ocr_preprocess_grayscale:
        processed = ImageOps.grayscale(processed)
    if settings.ocr_preprocess_contrast:
        processed = ImageEnhance.Contrast(processed).enhance(1.5)
    if settings.ocr_preprocess_threshold:
        processed = processed.point(lambda pixel: 255 if pixel > 180 else 0)
    if settings.ocr_preprocess_denoise:
        processed = processed.filter(ImageFilter.MedianFilter(size=3))
    return processed


def extract_text_from_image_bytes(content: bytes, settings: Settings) -> str:
    image = Image.open(BytesIO(content))
    processed = preprocess_image(image, settings)
    return normalize_block_text(pytesseract.image_to_string(processed, lang=settings.ocr_language))
