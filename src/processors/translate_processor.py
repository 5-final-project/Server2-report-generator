# src/processors/translate_processor.py
"""
영어 청크 → 한국어 번역 (Qwen-3-8B)
번역 결과를 콘솔 로그(INFO)로 확인할 수 있도록 구현
"""
from __future__ import annotations

import logging
import time
from typing import List

from src.api_clients.llm_client import LLMClient

log = logging.getLogger(__name__)


class TranslateProcessor:
    def __init__(
        self,
        client: LLMClient,
        *,
        retries: int = 3,
        backoff: float = 3.0,
    ) -> None:
        self.client = client
        self.retries = retries
        self.backoff = backoff
        self.sys = (
            "You are a professional translator. "
            "Translate the following text into accurate, natural Korean."
        )

    # ------------------------------------------------------
    def _translate_once(self, text: str) -> str:
        """Qwen API 한 번 호출"""
        return (
            self.client.generate(
                self.sys,
                text,
                max_tokens=1024,
                temperature=0.0,
            )
            .strip()
        )

    def run(self, chunks_en: List[str]) -> List[str]:
        translated: List[str] = []

        for idx, chunk in enumerate(chunks_en, start=1):
            for attempt in range(1, self.retries + 1):
                try:
                    ko = self._translate_once(chunk)
                    translated.append(ko)

                    # ▼ 콘솔 로그에 원문·번역 출력
                    src_preview = (chunk[:120] + "…") if len(chunk) > 120 else chunk
                    log.info(
                        "번역 %d/%d 완료\n  ├─ 원문: %s\n  └─ 번역: %s",
                        idx,
                        len(chunks_en),
                        src_preview.replace("\n", " "),
                        ko.replace("\n", " "),
                    )
                    break  # 성공하면 다음 청크로
                except Exception as exc:
                    if attempt == self.retries:
                        raise
                    time.sleep(self.backoff * attempt)

        return translated
