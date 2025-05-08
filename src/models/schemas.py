"""
src/models/schemas.py
────────────────────────────────────────────────────────────
• 허브-API 입력(JSON) → PipelineRequest
• 보고서 내부 사용 모델 → ReportSchema
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Optional

from pydantic import BaseModel, Field

# ──────────────── ⓐ  파이프라인(JSON) 입력용  ────────────────
class MeetingMeta(BaseModel):
    title: str
    datetime: datetime
    author: str
    participants: List[str]


class RelatedDoc(BaseModel):
    page_content: str
    metadata: Dict[str, str]
    score: Optional[float] = None


class Chunk(BaseModel):
    chunk_en: str
    related_docs: List[RelatedDoc]


class PipelineRequest(BaseModel):
    meeting_meta: MeetingMeta
    meeting_purpose: str
    insights: List[str]
    text_stt: str
    chunks: List[Chunk]
    all_documents: List[RelatedDoc]
    elapsed_time: float
    error: Optional[str] = None


# ──────────────── ⓑ  ReportBuilder 가 참조하는 타입  ──────────
class SearchDoc(BaseModel):
    """
    report_builder.py 의 `docs: list[SearchDoc]` 파라미터와
    하위 processor 들이 그대로 사용 중이므로 유지.
    실제 구조는 RelatedDoc 과 동일하지만
    호환성을 위해 별도 이름으로 남겨둔다.
    """
    page_content: str
    metadata: Dict[str, str]
    score: Optional[float] = None


# ──────────────── ⓒ  최종 보고서 모델  ──────────────────────
class ReportSchema(BaseModel):
    meeting_title: str = Field(..., max_length=200)
    executive_summary: str

    agenda_keypoints: List[str]
    decisions: List[str]
    action_items: List[str]
    risks: List[str]
    appendix: List[str]
