"""
FastAPI 엔드포인트
────────────────────────────────────────────────────────────
• POST /report-json   : 허브-API JSON → 보고서 생성
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pathlib import Path
import uuid

from src.models.schemas import PipelineRequest
from src.service.report_service import generate_report_from_pipeline_json

app = FastAPI(
    title="Report Generator API",
    version="1.0.0",
    description="허브-API JSON을 받아 HTML/PDF 회의록을 생성합니다.",
)


# ─────────────────────────── ❶ 보고서 생성 엔드포인트 ────────────────────────────
@app.post("/report-json", response_class=HTMLResponse,
          summary="허브-API JSON → HTML 보고서 생성")
def create_report_json(payload: PipelineRequest):
    """
    허브-API 가 내려주는 JSON( `PipelineRequest` )을 그대로 본문으로 보내면<br>
    HTML 보고서를 직접 반환합니다. PDF 파일은 `/report-pdf` 엔드포인트를 통해 접근할 수 있습니다.
    """
    out_dir = Path("/opt/app/out") / str(uuid.uuid4())
    try:
        paths = generate_report_from_pipeline_json(payload, out_dir)
        
        # HTML 파일 내용을 읽어서 직접 반환
        with open(paths["html"], "r", encoding="utf-8") as html_file:
            html_content = html_file.read()
        
        return html_content
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────── ❷ PDF 파일 제공 엔드포인트 ────────────────────────────
@app.post("/report-pdf", response_class=FileResponse,
          summary="허브-API JSON → PDF 보고서 생성")
def create_report_pdf(payload: PipelineRequest):
    """
    허브-API 가 내려주는 JSON( `PipelineRequest` )을 그대로 본문으로 보내면<br>
    PDF 보고서 파일을 직접 다운로드할 수 있게 반환합니다.
    """
    out_dir = Path("/opt/app/out") / str(uuid.uuid4())
    try:
        paths = generate_report_from_pipeline_json(payload, out_dir)
        
        # PDF 파일을 직접 반환 (다운로드 가능한 형태로)
        return FileResponse(
            path=paths["pdf"],
            media_type="application/pdf",
            filename="report.pdf"
        )
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))



