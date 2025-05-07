"""
src/cli.py
────────────────────────────────────────────────────────────
영어 STT → 한국어 PDF 회의 보고서 생성 파이프라인

    1. STT 텍스트 로드            (.txt / .jsonl)
    2. 4 000자 이하로 영어 청크 분할
    3. Qwen-8B 로 한국어 번역
    4. ─ ChunkRouter ─
         • USE_REMOTE_CHUNK=true  →  원격  /chunk-summarize-search
         • else                  →  로컬(Qwen) 요약
    5. VectorDB 유사 문서 검색으로 RAG 보강
    6. Qwen-8B 로 핵심 인사이트 추출
    7. Jinja2 + WeasyPrint 로 PDF 출력
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from config.settings import get_settings
from src.utils import load_lines, split_chunks

# ── API clients ───────────────────────────────────────────
from src.api_clients.chunk_client import ChunkClient
from src.api_clients.vector_client import VectorClient
from src.api_clients.llm_client import LLMClient

# ── Processors ────────────────────────────────────────────
from src.processors.translate_processor import TranslateProcessor
from src.processors.chunk_router import ChunkRouter          # ← router
from src.processors.search_processor import SearchProcessor
from src.processors.insight_extractor import InsightExtractor
from src.processors.report_builder import ReportBuilder

log = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Korean PDF meeting report from English STT text."
    )
    parser.add_argument("--stt", required=True, help="STT 파일 경로 (.txt 또는 .jsonl)")
    parser.add_argument("--out", required=True, help="출력 PDF 경로")
    args = parser.parse_args()

    stt_path = Path(args.stt).resolve()
    out_path = Path(args.out).resolve()
    cfg = get_settings()

    # ── API clients ───────────────────────────────────────
    chunk_cli = ChunkClient(cfg.CHUNK_API)
    vect_cli = VectorClient(cfg.VECTOR_API)
    llm_cli = LLMClient(cfg.LLM_API)

    # ── Processor chain ──────────────────────────────────
    tp = TranslateProcessor(llm_cli)
    cp = ChunkRouter(chunk_cli, llm_cli)          # ★ 라우터 사용
    sp = SearchProcessor(vect_cli)
    ie = InsightExtractor(llm_cli)
    rb = ReportBuilder(llm_cli)

    # 1) Load & split
    lines_en = load_lines(stt_path)
    chunks_en = split_chunks(lines_en)
    log.info("영어 청크 수: %d", len(chunks_en))

    # 2) Translate
    chunks_ko = tp.run(chunks_en)

    # 3) Summarize (remote or local)  +  docs(optional)
    summaries, sim_docs = cp.run(chunks_ko)

    # 4) Vector search
    extra_docs = sp.run(summaries, k=5)
    all_docs = sim_docs + extra_docs

    # 5) Insight extraction
    insights = ie.run(summaries)

    # 6) PDF export
    rb.build_pdf(summaries, all_docs, insights, out_path)
    log.info("PDF 저장 완료 → %s", out_path)


if __name__ == "__main__":
    main()
