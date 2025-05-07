"""
/chunk-summarize-search API 전용 클라이언트
"""
from typing import Any
from src.api_clients.base import BaseClient


class ChunkClient(BaseClient):
    def __init__(self, base_url: str) -> None:
        # add_auth=False  → Authorization 헤더 제거
        super().__init__(base_url, add_auth=False, extra_headers=None)

    # ----------------------------------------------------------
    def chunk_summarize_search(
        self,
        text: str,
        num_clusters: int = 5,
    ) -> dict[str, Any]:
        body = {"text": text, "num_clusters": num_clusters}
        return self._post("/chunk-summarize-search", body)
