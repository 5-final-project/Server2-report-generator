"""
FastAPI 엔드포인트
────────────────────────────────────────────────────────────
• POST /report-json   : 허브-API JSON → 보고서 생성
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid

from src.models.schemas import PipelineRequest
from src.service.report_service import generate_report_from_pipeline_json

app = FastAPI(
    title="Report Generator API",
    version="1.0.0",
    description="허브-API JSON을 받아 HTML/PDF 회의록을 생성합니다.",
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



