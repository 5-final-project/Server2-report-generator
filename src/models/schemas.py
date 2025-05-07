from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class SearchDoc(BaseModel):
    page_content: str
    metadata: Dict[str, str]
    score: Optional[float] = None


class ReportSchema(BaseModel):
    """
    최종 보고서 JSON 스키마.
    LLM 출력 → Pydantic 검증 → HTML 렌더링에 사용.
    """

    meeting_title: str = Field(..., max_length=200)
    executive_summary: str

    agenda_keypoints: List[str]
    decisions: List[str]
    action_items: List[str]
    risks: List[str]
    appendix: List[str]
