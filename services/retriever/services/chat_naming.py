from __future__ import annotations

import secrets


def generate_chat_name() -> str:
    return f"chat-{secrets.token_hex(3)}"
