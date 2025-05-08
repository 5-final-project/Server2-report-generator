"""
src/service/report_service.py
────────────────────────────────────────────────────────────
CLI · FastAPI 가 공통으로 호출하는 비즈니스 로직
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict

from config.settings import get_settings
from src.api_clients.gemini_client import GeminiClient
from src.processors.summary_processor import SummaryProcessor
from src.processors.action_processor import ActionProcessor
from src.processors.integrated_analysis_processor import IntegratedAnalysisProcessor
from src.processors.report_builder import ReportBuilder
from src.models.schemas import ReportSchema, MeetingMeta, SearchDoc  # SearchDoc 복구됨


_cfg = get_settings()
_gem = GeminiClient(_cfg.LLM_API)


def _build_report_model(p: PipelineRequest,
                        summary: str,
                        actions: list[str],
                        analysis: str) -> ReportSchema:
    return ReportSchema(
        meeting_title=p.meeting_meta.title,
        executive_summary=summary,
        agenda_keypoints=p.insights,
        decisions=[],
        action_items=actions,
        risks=[],
        appendix=[analysis],
    )


def generate_report_from_pipeline_json(
        p: PipelineRequest,
        out_dir: Path) -> Dict[str, Path]:
    """
    허브-API JSON(PipelineRequest) → Gemini → HTML·PDF 생성
    반환: {"html": Path, "pdf": Path}
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "report.html"
    pdf_path  = out_dir / "report.pdf"

    # ─ Gemini 요약/액션/통합 분석 ─
    summary   = SummaryProcessor(_gem).run(p.text_stt)
    actions   = ActionProcessor(_gem).run(p.text_stt)
    analysis  = IntegratedAnalysisProcessor(_gem).run(
        p.text_stt,
        [d.model_dump() for d in p.all_documents],
    )

    report_m  = _build_report_model(p, summary, actions, analysis)

    # ─ HTML + PDF ─
    ReportBuilder().build_report(
        report=report_m,
        meta=p.meeting_meta,
        purpose=p.meeting_purpose,
        docs=p.all_documents,
        out_pdf=pdf_path,
        out_html=html_path,
    )

    return {"html": html_path, "pdf": pdf_path}
