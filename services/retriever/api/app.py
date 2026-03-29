from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.common.config import get_settings
from services.retriever.api.dependencies import get_retriever_service
from services.retriever.schemas.chat import ChatRead, ErrorResponse, HealthResponse, MessageCreateRequest, MessageCreateResponse, MessageRead
from services.retriever.services.retriever_service import RetrieverAppService


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Local RAG Retriever API", version="3.0.0")

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

    return app
