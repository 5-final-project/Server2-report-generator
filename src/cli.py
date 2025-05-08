"""
src/cli.py
────────────────────────────────────────────────────────────
단일 Pipeline API → Gemini 요약/액션/분석 → HTML + PDF 회의록
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from config.settings import get_settings
from src.api_clients.pipeline_client import PipelineClient
from src.api_clients.gemini_client import GeminiClient

from src.processors.summary_processor import SummaryProcessor
from src.processors.action_processor import ActionProcessor
from src.processors.integrated_analysis_processor import IntegratedAnalysisProcessor
from src.processors.report_builder import ReportBuilder
from src.models.schemas import PipelineResponse, ReportSchema

log = logging.getLogger(__name__)


def _args() -> argparse.Namespace:
    p = argparse.ArgumentParser("Generate meeting report")
    p.add_argument("--stt", required=True, help="STT 원문(.txt)")
    p.add_argument("--out", required=True, help="출력 PDF 경로 (HTML은 동일 이름)")
    p.add_argument("--clusters", type=int, default=5)
    p.add_argument("--topk", type=int, default=5)
    return p.parse_args()


def main() -> None:
    args = _args()
    cfg = get_settings()

    stt_path = Path(args.stt).resolve()
    out_pdf = Path(args.out).resolve()

    hub = PipelineClient(cfg.PIPELINE_API)
    gem = GeminiClient(cfg.LLM_API)

    # ------------ 0) Pipeline API
    log.info("📡 Pipeline API 호출…")
    raw = hub.run(
        text_stt=stt_path.read_text(encoding="utf-8"),
        num_clusters=args.clusters,
        top_k=args.topk,
        target_lang="ko",
    )
    data: PipelineResponse = PipelineResponse.model_validate(raw)

    # ------------ 1) Gemini
    summary = SummaryProcessor(gem).run(data.text_stt)
    actions = ActionProcessor(gem).run(data.text_stt)
    analysis = IntegratedAnalysisProcessor(gem).run(
        data.text_stt, [d.model_dump() for d in data.all_documents]
    )

    # ------------ 2) ReportSchema
    report = ReportSchema(
        meeting_title=data.meeting_meta.title,
        executive_summary=summary,
        agenda_keypoints=data.insights,
        decisions=[],
        action_items=actions,
        risks=[],
        appendix=[analysis],
    )

    # ------------ 3) build
    ReportBuilder().build_report(
        report=report,
        meta=data.meeting_meta,
        purpose=data.meeting_purpose,
        docs=data.all_documents,
        out_pdf=out_pdf,
    )


if __name__ == "__main__":
    main()
