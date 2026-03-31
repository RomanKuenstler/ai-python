from __future__ import annotations

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from services.embedder.api.dependencies import get_attachment_processing_service
from services.embedder.attachment_service import AttachmentJobFile, AttachmentProcessingService


class AttachmentJobFileRequest(BaseModel):
    file_name: str
    content_base64: str


class AttachmentJobRequest(BaseModel):
    type: str = Field(default="attachment_processing")
    files: list[AttachmentJobFileRequest] = Field(default_factory=list)


class AttachmentRead(BaseModel):
    file_name: str
    content: str
    type: str
    extraction_method: str | None = None
    quality: dict = Field(default_factory=dict)


class AttachmentJobResponse(BaseModel):
    attachments: list[AttachmentRead] = Field(default_factory=list)


def create_app() -> FastAPI:
    app = FastAPI(title="Local RAG Embedder API", version="5.0.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/internal/process-attachments", response_model=AttachmentJobResponse)
    def process_attachments(
        payload: AttachmentJobRequest,
        service: AttachmentProcessingService = Depends(get_attachment_processing_service),
    ) -> AttachmentJobResponse:
        attachments = service.process_files([AttachmentJobFile(**file.model_dump()) for file in payload.files])
        return AttachmentJobResponse(attachments=attachments)

    return app
