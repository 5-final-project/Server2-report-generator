from typing import List
from src.api_clients.llm_client import LLMClient

class SummaryProcessor:
    """회의 내용을 한국어로 요약 (3~5줄)"""

    SYS = (
        "당신은 전문 비즈니스 회의 요약가입니다. "
        "사용자가 제공한 영어 회의 원문을 읽고 한국어로 3~5문장 핵심 요약을 작성하세요."
    )

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def run(self, text_en: str) -> str:
        return self.client.generate(
            system_prompt=self.SYS,
            user_prompt=text_en,
            max_tokens=512,
            temperature=0.3,
        )
