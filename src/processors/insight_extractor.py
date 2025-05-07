from typing import List
from src.api_clients.llm_client import LLMClient
class InsightExtractor:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def run(self, chunk_summaries: List[str], n: int = 5) -> List[str]:
        sys_msg = (
            "너는 회의를 분석하는 전문가이다. "
            f"다음 요약들을 참고하여 핵심 인사이트 {n}개를 bullet list로 작성하라."
        )
        user_msg = "\n\n".join(chunk_summaries)

        text = self.client.generate(sys_msg, user_msg, max_tokens=256)
        return [
            line.lstrip("•- ").strip()
            for line in text.splitlines()
            if line.strip()
        ][:n]
