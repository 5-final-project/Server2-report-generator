# src/models/schemas.py
# ────────────────────────────────────────────────────────────
"""Pydantic 데이터 스키마 정의"""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field


# ────────────────────────────────────────────────────────────
class SearchDoc(BaseModel):
    """벡터 탐색/유사 문서 결과 1건"""
    page_content: str
    metadata: Dict[str, str]
    score: Optional[float] = None


# ────────────────────────────────────────────────────────────
class MeetingMeta(BaseModel):
    """회의 기본 정보(머리글)"""
    title: str = Field(..., max_length=200)
    datetime: datetime | str                # ISO-8601 문자열도 허용
    author: str
    participants: List[str]


# ────────────────────────────────────────────────────────────
class PipelineResponse(BaseModel):
    """
    단일 Pipeline API 응답 스키마
    (sample_pipeline.json 과 동일 구조)
    """
    meeting_meta: MeetingMeta
    meeting_purpose: str
    insights: List[str]                     # = 핵심 인사이트(주요 논의 내용)
    text_stt: str                           # STT 원문(영어)
    all_documents: List[SearchDoc]          # 사내 문서 컨텍스트

    # 선택 필드
    chunks: Optional[List[Dict[str, Any]]] = None
    elapsed_time: Optional[float] = None
    error: Optional[str] = None


# ────────────────────────────────────────────────────────────
class ReportSchema(BaseModel):
    """
    최종 회의 보고서(JSON) 스키마  
    Gemini 결과 → Pydantic 검증 → HTML/PDF 렌더링에 사용
    """
    meeting_title: str = Field(..., max_length=200)
    executive_summary: str

    agenda_keypoints: List[str]             # 주요 논의(=핵심 인사이트)
    decisions: List[str] = []
    action_items: List[str] = []
    risks: List[str] = []
    appendix: List[str] = []
