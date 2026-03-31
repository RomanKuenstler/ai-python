from __future__ import annotations

from dotenv import load_dotenv
import uvicorn

from services.common.config import get_settings
from services.common.logging import configure_logging


def main() -> None:
    load_dotenv()
    settings = get_settings()
    configure_logging(settings.log_level)
    uvicorn.run(
        "services.retriever.api.app:create_app",
        host=settings.api_host,
        port=settings.api_port,
        factory=True,
    )


if __name__ == "__main__":
    main()
