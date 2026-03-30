from __future__ import annotations

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from services.common.config import get_settings
from services.retriever.api.dependencies import get_retriever_service
from services.retriever.schemas.chat import (
    ChatRead,
    ChatUpdateRequest,
    ErrorResponse,
    HealthResponse,
    LibraryFileRead,
    LibraryFileUpdateRequest,
    LibraryListResponse,
    LibraryUploadResponse,
    MessageCreateRequest,
    MessageCreateResponse,
    MessageRead,
)
from services.retriever.services.library_manager import UploadFilePayload
from services.retriever.services.retriever_service import RetrieverAppService


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Local RAG Retriever API", version="4.0.0")

    origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/api/chats", response_model=ChatRead)
    def create_chat(service: RetrieverAppService = Depends(get_retriever_service)) -> ChatRead:
        return service.create_chat()

    @app.get("/api/chats", response_model=list[ChatRead])
    def list_chats(service: RetrieverAppService = Depends(get_retriever_service)) -> list[ChatRead]:
        return service.list_chats()

    @app.get("/api/chats/{chat_id}", response_model=ChatRead, responses={404: {"model": ErrorResponse}})
    def get_chat(chat_id: str, service: RetrieverAppService = Depends(get_retriever_service)) -> ChatRead:
        chat = service.get_chat(chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat

    @app.patch("/api/chats/{chat_id}", response_model=ChatRead, responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}})
    def rename_chat(
        chat_id: str,
        payload: ChatUpdateRequest,
        service: RetrieverAppService = Depends(get_retriever_service),
    ) -> ChatRead:
        try:
            chat = service.rename_chat(chat_id, payload.chat_name)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat

    @app.delete("/api/chats/{chat_id}", response_model=ChatRead, responses={404: {"model": ErrorResponse}})
    def delete_chat(chat_id: str, service: RetrieverAppService = Depends(get_retriever_service)) -> ChatRead:
        chat = service.delete_chat(chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat

    @app.get("/api/chats/{chat_id}/messages", response_model=list[MessageRead], responses={404: {"model": ErrorResponse}})
    def get_messages(chat_id: str, service: RetrieverAppService = Depends(get_retriever_service)) -> list[MessageRead]:
        chat = service.get_chat(chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return service.get_chat_messages(chat_id)

    @app.post(
        "/api/chats/{chat_id}/messages",
        response_model=MessageCreateResponse,
        responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    )
    def create_message(
        chat_id: str,
        payload: MessageCreateRequest,
        service: RetrieverAppService = Depends(get_retriever_service),
    ) -> MessageCreateResponse:
        result = service.send_message(chat_id, payload.content.strip())
        if result is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return MessageCreateResponse(**result)

    @app.get("/api/library/files", response_model=LibraryListResponse)
    def list_library_files(service: RetrieverAppService = Depends(get_retriever_service)) -> LibraryListResponse:
        return service.list_library_files()

    @app.post("/api/library/files/upload", response_model=LibraryUploadResponse, responses={422: {"model": ErrorResponse}})
    async def upload_library_files(
        files: list[UploadFile] = File(...),
        tags_by_file: str | None = Form(default=None),
        service: RetrieverAppService = Depends(get_retriever_service),
    ) -> LibraryUploadResponse:
        uploads = [UploadFilePayload(file_name=file.filename or "upload.bin", content=await file.read()) for file in files]
        try:
            return LibraryUploadResponse(**service.upload_library_files(uploads, tags_by_file))
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.patch(
        "/api/library/files/{file_id}",
        response_model=LibraryFileRead,
        responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    )
    def update_library_file(
        file_id: int,
        payload: LibraryFileUpdateRequest,
        service: RetrieverAppService = Depends(get_retriever_service),
    ) -> LibraryFileRead:
        if payload.is_enabled is None:
            raise HTTPException(status_code=422, detail="At least one file field must be updated")
        record = service.update_library_file(file_id, is_enabled=payload.is_enabled)
        if record is None:
            raise HTTPException(status_code=404, detail="Library file not found")
        return record

    @app.delete("/api/library/files/{file_id}", response_model=LibraryFileRead, responses={404: {"model": ErrorResponse}})
    def delete_library_file(file_id: int, service: RetrieverAppService = Depends(get_retriever_service)) -> LibraryFileRead:
        record = service.delete_library_file(file_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Library file not found")
        return record

    return app
