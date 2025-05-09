"""
src/models/schemas.py
────────────────────────────────────────────────────────────
모든 Pydantic 모델 정의 (FastAPI 입력·출력, 내부 처리 공용)

● 변경 / 보강
  1. metadata → Dict[str, Any] 로 완전 개방  
     ─ 숫자·문자 혼재 자료 수용, 422 오류 해결
  2. Pydantic v2 양식 적용 (model_config = ConfigDict …)
  3. 서버용 요청 모델 `PipelineRequest` 추가
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, StrictStr


# ────────────────────────────── 검색 결과 · 문서 ─────────────────────────────
class SearchDoc(BaseModel):
    """
    벡터 검색으로 회수된 1개의 문서.
    metadata 는 페이지·점수·PDF 속성 등 구조가 가변적이므로
    Dict[str, Any] 로 전면 허용.
    """

    page_content: StrictStr
    metadata: Dict[str, Any] = Field(default_factory=dict)
    score: float

    # 예기치 못한 필드 무시
    model_config = ConfigDict(extra="allow")


class ChunkDoc(BaseModel):
    """
    STT 내 한 ‘문단’(chunk) + 연결된 관련 문서들
    """

    chunk_en: StrictStr
    related_docs: List[SearchDoc] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


# ────────────────────────────── 파이프라인 원본 구조 ─────────────────────────
class MeetingMeta(BaseModel):
    title: StrictStr
    datetime: datetime
    author: StrictStr
    participants: List[StrictStr]

    model_config = ConfigDict(extra="allow")


class PipelineResponse(BaseModel):
    """
    사내 Pipeline API(또는 테스트용 sample_pipeline.json) →
    애플리케이션으로 넘어오는 원본 데이터 스키마
    """

    meeting_meta: MeetingMeta
    meeting_purpose: StrictStr
    insights: List[StrictStr]
    text_stt: StrictStr

    chunks: List[ChunkDoc] = Field(default_factory=list)
    all_documents: List[SearchDoc] = Field(default_factory=list)

    elapsed_time: float
    error: Optional[str] = None

    model_config = ConfigDict(extra="allow")


# FastAPI 요청 본문 검증용 별칭 (현재 구조가 동일해 그대로 상속)
class PipelineRequest(PipelineResponse):
    """POST /report-json 요청 바디"""

    pass


# ────────────────────────────── ReportBuilder 입력 ──────────────────────────
class ReportSchema(BaseModel):
    """
    ReportBuilder 가 소비하는 최소·정규화 데이터 구조
    (PipelineResponse → 요약·액션·분석 결과를 합쳐 재구성)
    """

    meeting_title: StrictStr
    executive_summary: StrictStr
    agenda_keypoints: List[StrictStr]
    decisions: List[StrictStr]
    action_items: List[StrictStr]
    risks: List[StrictStr]
    appendix: List[StrictStr]

    model_config = ConfigDict(extra="allow")
