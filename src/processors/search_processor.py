"""
벡터 검색 리콜 보강 + 중복 제거
"""
from typing import List, Dict, Any, Set, Tuple
from src.api_clients.vector_client import VectorClient
class SearchProcessor:
    def __init__(self, client: VectorClient) -> None:
        self.client = client

    def run(
        self,
        queries: List[str],
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for q in queries:
            results.extend(self.client.search_with_score(q, k))

        # 점수순 정렬
        results.sort(key=lambda d: -(d.get("score") or 0))

        # 중복 제거
        seen: Set[Tuple[str, str]] = set()
        uniques: List[Dict[str, Any]] = []
        for doc in results:
            uid = (
                doc["metadata"].get("path"),
                doc["metadata"].get("chunk_id"),
            )
            if uid in seen:
                continue
            seen.add(uid)
            uniques.append(doc)
        return uniques[:k]

