"""
회의 STT 청크 → 요약 + 유사 문서 수집

· 요청 : POST /chunk-summarize-search
          {"text": <chunk>, "num_clusters": 5}
· 응답 : {"result": [ { "summary", "similar_documents", "error", … }, … ]}

결과를 두 리스트(summaries, documents)에 누적해 반환한다.
"""
from __future__ import annotations
from typing import List, Tuple, Dict, Any
from src.api_clients.chunk_client import ChunkClient

class ChunkProcessor:
    def __init__(self, client: ChunkClient) -> None:
        self.client = client

    def run(
        self,
        chunks: List[str],
        num_clusters: int = 5,
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        summaries: List[str] = []
        documents: List[Dict[str, Any]] = []

        for ch in chunks:
            payload = self.client.chunk_summarize_search(ch, num_clusters)
            for item in payload.get("result", []):
                if item.get("error"):
                    raise RuntimeError(item["error"])
                summaries.append(item.get("summary", ""))
                documents.extend(item.get("similar_documents") or [])
        return summaries, documents
