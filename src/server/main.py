"""
FastAPI 엔드포인트
────────────────────────────────────────────────────────────
• POST /report-json   : 허브-API JSON → 보고서 생성
• (기존) /report      : STT 텍스트 파일 업로드 버전
"""

from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
import shutil

from src.models.schemas import PipelineRequest
from src.service.report_service import generate_report_from_pipeline_json

app = FastAPI(
    title="Report Generator API",
    version="1.0.0",
    description="허브-API JSON 또는 STT 파일을 받아 HTML/PDF 회의록을 생성합니다.",
)


# ─────────────────────────── ❶ JSON 기반 엔드포인트 ────────────────────────────
@app.post("/report-json", response_class=JSONResponse,
          summary="허브-API JSON → 보고서 생성")
def create_report_json(payload: PipelineRequest):
    """
    허브-API 가 내려주는 JSON( `PipelineRequest` )을 그대로 본문으로 보내면<br>
    `/out/<uuid>/report.html`, `/report.pdf` 두 파일이 생성되고<br>
    해당 경로를 JSON 으로 돌려줍니다.
    """
    out_dir = Path("/opt/app/out") / str(uuid.uuid4())
    try:
        paths = generate_report_from_pipeline_json(payload, out_dir)
        return {"html": str(paths["html"]), "pdf": str(paths["pdf"])}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────── ❷ (호환용) 파일 업로드 방식 ────────────────────────
@app.post("/report", response_class=JSONResponse,
          summary="STT(.txt) 파일 업로드 → 보고서 생성 (기존 방식)")
def create_report(
    stt_file: UploadFile = File(..., description="회의 STT 텍스트(.txt)"),
    clusters: int = Form(5, ge=2, description="클러스터 수"),
    top_k: int = Form(5, ge=1, description="문서 검색 Top-K"),
):
    """
    ➡️ 기존 CLI 흐름을 API 로 그대로 노출한 엔드포인트  
    (허브-API JSON 이 준비되면 /report-json 을 사용하세요)
    """
    # 업로드 파일 저장
    tmp_txt = Path("/tmp") / f"{uuid.uuid4()}.txt"
    with tmp_txt.open("wb") as f:
        shutil.copyfileobj(stt_file.file, f)

    # CLI 와 같은 파이프라인 호출 (생략: 예시용 dummy 응답)
    return {"html": None, "pdf": None, "detail": "Use /report-json instead."}
