from typing import List
from src.api_clients.llm_client import LLMClient

class ActionProcessor:
    """회의에서 결정된 Action Item 한국어 추출"""

    SYS = (
        "아래 회의 기록(영어)에서 실행해야 할 구체적 Action Item을 한국어 bullet 리스트로 뽑아주세요. "
        "• 형태의 글머리표만 사용하고, 각 항목은 간결한 명령문으로 작성하세요."
    )

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def run(self, text_en: str) -> List[str]:
        bullets = self.client.generate(
            system_prompt=self.SYS,
            user_prompt=text_en,
            max_tokens=256,
            temperature=0.2,
        )
        return [b.lstrip("• ").strip() for b in bullets.splitlines() if b.strip()]
