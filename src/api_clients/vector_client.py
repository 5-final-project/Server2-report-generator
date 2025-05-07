from typing import Any, Dict, List, Optional
from .base import BaseClient


class VectorClient(BaseClient):
    """POST /search_score : {"keywords":[str],"k":int,"filter":{}}"""

    def search_with_score(
        self,
        query: str,
        k: int = 5,
        filter_: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        body = {
            "keywords": [query],
            "k": k,
            "filter": filter_ or {},
        }
        data = self._post("/search_score", body)
        return data.get("results", [])
