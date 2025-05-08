"""
src/api_clients/gemini_client.py
────────────────────────────────────────────────────────────
Google Generative Language API – Gemini 1.5 Flash 전용 클라이언트
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx
from pydantic import AnyUrl

from config.settings import get_settings
from .base import BaseClient

log = logging.getLogger(__name__)


class GeminiClient(BaseClient):
    """
    엔드포인트 예시
      https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest
    """

    def __init__(self, base_url: str | AnyUrl, api_key: Optional[str] = None) -> None:
        self._api_key: str = api_key or get_settings().API_KEY
        if not self._api_key:
            raise ValueError("Google Gemini API_KEY 가 설정되지 않았습니다.")

        # BaseClient 에서는 인증 헤더가 불필요
        super().__init__(str(base_url).rstrip("/"), add_auth=False)

        # 완전한 호출 URL을 미리 만들어 둔다
        self._gen_url: str = f"{self.base_url}:generateContent"

    # ----------------------------------------------------------- helpers
    def _post_gen(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        /:generateContent POST 래퍼
        * API-KEY 는 `key` 쿼리스트링으로 전달해야 400 오류가 발생하지 않는다.
        """
        resp = self.session.post(self._gen_url, params={"key": self._api_key}, json=payload)
        resp.raise_for_status()
        return resp.json()

    # ----------------------------------------------------------- public
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.8,
        top_p: float = 0.95,
    ) -> str:
        """
        system + user 프롬프트를 하나로 묶어 user 역할로 전송.
        예외 발생 시 RuntimeError 로 전파해 전체 파이프라인을 즉시 중단한다.
        """
        body: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}],
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
                "topP": top_p,
            },
        }

        try:
            data = self._post_gen(body)
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as exc:  # httpx.HTTPError | KeyError | IndexError
            # Gemini 실패는 더 이상 허용하지 않음 → 즉시 오류 전파
            log.error("Gemini 호출 실패 – 파이프라인 중단: %s", exc)
            raise RuntimeError("🛑 Gemini API 호출 실패 – 작업을 중단합니다.") from exc
