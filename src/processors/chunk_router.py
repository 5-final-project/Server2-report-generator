# src/processors/chunk_router.py
"""
ChunkRouter
────────────────────────────────────────────────────────────
`/chunk-summarize-search` 원격 호출과 **동일한 출력 형식**을
유지하면서, 서버 장애 시 로컬(Qwen) 요약으로 자동 대체한다.

반환 튜플은 언제나
    summaries : List[str]              # 각 청크의 요약
    documents : List[dict[str, Any]]   # Chunk API의 similar_documents

환경변수
────────
USE_REMOTE_CHUNK=true   →  원격 Chunk API 사용 (ChunkProcessor)
(없음 또는 false)       →  로컬 요약 (LocalChunkProcessor)

로컬 요약 모드는 유사 문서를 바로 얻을 수 없으므로
documents 리스트를 빈 배열([])로 반환한다.
SearchProcessor 단계에서 Vector API가 documents 를
추가로 보강하므로 다운스트림 인터페이스가 깨지지 않는다.
"""
from __future__ import annotations

import os
from typing import List, Tuple, Dict, Any

from src.processors.chunk_processor import ChunkProcessor          # 원격
from src.processors.local_chunk_processor import LocalChunkProcessor  # 로컬
from src.api_clients.chunk_client import ChunkClient
from src.api_clients.llm_client import LLMClient


class ChunkRouter:
    """런타임에 두 백엔드 중 하나를 선택해 호출"""

    def __init__(
        self,
        chunk_client: ChunkClient,
        llm_client: LLMClient,
    ) -> None:
        use_remote = os.getenv("USE_REMOTE_CHUNK", "false").lower() == "true"

        if use_remote:
            self.backend = ChunkProcessor(chunk_client)
        else:
            self.backend = LocalChunkProcessor(llm_client)

    # ----------------------------------------------------------
    def run(
        self,
        chunks_ko: List[str],
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        returns
            summaries : list[str]
            documents : list[dict]   (empty list when local mode)
        """
        return self.backend.run(chunks_ko)
