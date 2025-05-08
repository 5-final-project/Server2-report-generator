from enum import StrEnum


class Role(StrEnum):
    """LLM Chat 메시지 역할 Enum."""
    SYSTEM = "system"
    USER = "user"
