"""
src/api_clients/pipeline_client.py
────────────────────────────────────────────────────────────
단일 Pipeline API 클라이언트
▸ 실제 서버가 없으면 /opt/app/data/sample_pipeline.json 로 폴백
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

import httpx
from .base import BaseClient

log = logging.getLogger(__name__)

# 샘플 JSON 위치 (docker-compose 에서 /opt/app/data 로 마운트)
_SAMPLE_FILE = Path("/opt/app/data/sample_pipeline.json")


class PipelineClient(BaseClient):
    """
    • /pipeline-run 엔드포인트 호출
    • 404·연결 오류 시 로컬 샘플 JSON 반환
    """

    def __init__(self, base_url: str) -> None:
        # Pipeline API 는 인증 불필요
        super().__init__(base_url, add_auth=False)

    # ------------------------------------------------------
    def run(
        self,
        *,
        text_stt: str,
        num_clusters: int,
        top_k: int,
        target_lang: str,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "text_stt": text_stt,
            "num_clusters": num_clusters,
            "top_k": top_k,
            "target_lang": target_lang,
        }

        try:
            return self._post("/pipeline-run", body)

        # ───────── 폴백: 로컬 샘플 JSON ─────────
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                log.warning(
                    "🔄 Pipeline API 404 – 샘플 파일로 폴백: %s", _SAMPLE_FILE
                )
                return self._load_sample()
            raise  # 다른 HTTP 오류는 그대로 전파

        except (httpx.RequestError, httpx.TimeoutException) as exc:
            log.warning("🔄 Pipeline API 연결 실패 – 샘플 파일 사용: %s", exc)
            return self._load_sample()

    # ------------------------------------------------------
    @staticmethod
    def _load_sample() -> Dict[str, Any]:
        if not _SAMPLE_FILE.exists():
            raise FileNotFoundError(
                f"Sample file not found: {_SAMPLE_FILE}. "
                "테스트용 sample_pipeline.json 을 준비하세요."
            )
        return json.loads(_SAMPLE_FILE.read_text(encoding="utf-8"))
