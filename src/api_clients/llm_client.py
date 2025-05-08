"""
⚠️  레거시 호환용 래퍼 파일  ⚠️
────────────────────────────────────────────────────────────
기존 코드가 `from src.api_clients.llm_client import LLMClient`
형태로 임포트하므로, 새롭게 만든 GeminiClient 클래스를
alias 로 재노출한다.
"""
from __future__ import annotations

from .gemini_client import GeminiClient

# 기존 이름 유지
LLMClient = GeminiClient

__all__ = ["LLMClient", "GeminiClient"]
