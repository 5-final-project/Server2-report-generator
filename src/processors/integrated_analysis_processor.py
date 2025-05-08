from typing import List, Dict, Any
from src.api_clients.llm_client import LLMClient

class IntegratedAnalysisProcessor:
    """회의·문서를 종합한 한국어 인사이트"""

    SYS = (
        "다음 두 가지 정보를 모두 고려하여 한국어로 5줄 이내로 통합 분석을 작성하세요.\n"
        "1) 회의 영어 원문\n2) 관련 사내 문서(콘텍스트)"
    )

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def run(self, meeting_text_en: str, docs: List[Dict[str, Any]]) -> str:
        doc_snippets = "\n\n".join(d["page_content"][:800] for d in docs[:10])
        user = f"## 회의 원문\n{meeting_text_en}\n\n## 문서\n{doc_snippets}"
        return self.client.generate(
            system_prompt=self.SYS,
            user_prompt=user,
            max_tokens=512,
            temperature=0.25,
        )
