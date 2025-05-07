"""
src/processors/local_chunk_processor.py
────────────────────────────────────────────────────────────
Chunk API가 사용 불가능할 때를 대비한 **로컬 요약 대체 프로세서**.

● 입력  : 한국어 청크(List[str])
● 출력  : (summaries, documents)
          ├─ summaries : 각 청크를 2문장으로 요약한 문자열 리스트
          └─ documents : 빈 리스트([])   ← 유사 문서는 Vector 검색 단계에서 보강

Gemini/Chunk API 대신 Qwen-3-8B 모델을 직접 호출하여
동일한 인터페이스(summaries, docs)를 유지한다.
"""
from __future__ import annotations

from typing import List, Tuple, Dict, Any
from src.api_clients.llm_client import LLMClient


class LocalChunkProcessor:
    """Qwen 모델로 간단 요약"""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm
        self.sys_prompt = (
            "너는 회의록을 요약하는 전문가다. "
            "사용자가 보낸 한국어 텍스트를 두 문장으로 간결하게 요약하라."
        )

    # ------------------------------------------------------
    def run(
        self, chunks_ko: List[str]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """로컬 요약 실행

        Returns
        -------
        summaries : List[str]
            각 청크의 2문장 요약
        documents : List[dict]
            빈 리스트 (Vector 검색 단계에서 보강)
        """
        summaries: List[str] = [
            self.llm.generate(
                self.sys_prompt, chunk, max_tokens=256, temperature=0.3
            ).strip()
            for chunk in chunks_ko
        ]

        return summaries, []  # Chunk API와 형식 맞추기 위해 빈 리스트 반환
