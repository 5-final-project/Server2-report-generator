from enum import StrEnum


class Role(StrEnum):
    """
    LLM Chat 메시지 역할 Enum.
    StrEnum → 직렬화 시 문자열 그대로 사용 가능.
    """

    SYSTEM = "system"
    USER = "user"
