"""
src/processors/report_builder.py
────────────────────────────────────────────────────────────
Qwen GGUF REST 서버에서 받은 function-call / 자연어 혼합 응답 → PDF

▸ 가능한 응답 포맷
    1) text = '{"name":"make_report","arguments":{…}}'
    2) text = '무슨 설명… ```json\n{ ... }\n``` …'
    3) text = '{ ... }'   (JSON만 단독)

모든 경우를 처리하도록 fallback 로직을 추가했다.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from src.api_clients.llm_client import LLMClient
from src.models.schemas import ReportSchema
from config.settings import get_settings

log = logging.getLogger(__name__)

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)  # 가장 바깥 {...}


class ReportBuilder:
    def __init__(self, client: LLMClient) -> None:
        self.client = client
        cfg = get_settings()
        self.env = Environment(
            loader=FileSystemLoader(cfg.TEMPLATE_DIR),
            autoescape=select_autoescape(),
        )

    # ────────────────────────────── helpers
    @staticmethod
    def _extract_json_block(text: str) -> dict[str, Any]:
        """임의의 문자열에서 첫 JSON 객체 추출 → dict"""
        match = _JSON_BLOCK_RE.search(text)
        if not match:
            raise ValueError("JSON 블록을 찾을 수 없습니다.")
        return json.loads(match.group())

    # ────────────────────────────── core
    def _gen_report_json(
        self,
        summaries: List[str],
        docs: List[Dict[str, Any]],
        insights: List[str],
    ) -> ReportSchema:
        schema_json = ReportSchema.model_json_schema()

        sys_prompt = (
            "너는 구조화된 회의 보고서를 작성하는 전문가다. "
            "반드시 make_report 함수를 호출하여 JSON만 반환하라."
        )
        user_prompt = (
            "### 회의 요약\n"
            f"{chr(10).join(summaries)}\n\n"
            "### 관련 문서\n"
            f"{chr(10).join(d['page_content'][:800] for d in docs)}\n\n"
            "### 핵심 인사이트\n"
            f"{chr(10).join(insights)}"
        )

        resp = self.client.generate_with_tools(
            schema=schema_json,
            user_content=user_prompt,
            system_prompt=sys_prompt,
            max_tokens=2048,
            temperature=0.0,
        )

        raw_text: str = resp.get("text", "").strip()
        if not raw_text:
            raise RuntimeError("Qwen 응답에 text 필드가 없습니다.")

        # ─ 1단계: 바로 JSON 파싱 시도
        parsed: dict[str, Any] | None = None
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            # 자연어+JSON 혼합 → 정규식으로 추출
            try:
                parsed = self._extract_json_block(raw_text)
            except Exception as exc:
                raise RuntimeError("JSON 추출 실패") from exc

        # parsed 는 {"name": "...", "arguments": {…}} 또는 곧바로 arguments dict
        if "arguments" in parsed:
            arguments_raw = parsed["arguments"]
        else:
            arguments_raw = parsed  # 이미 target schema 일치

        arguments = (
            arguments_raw
            if isinstance(arguments_raw, dict)
            else json.loads(arguments_raw)
        )

        report = ReportSchema.model_validate(arguments)
        log.info("🗒️  Report JSON 검증 성공 – keys=%d", len(arguments))
        return report

    # ────────────────────────────── public
    def build_pdf(
        self,
        summaries: List[str],
        docs: List[Dict[str, Any]],
        insights: List[str],
        out_path: Path,
    ) -> Path:
        report = self._gen_report_json(summaries, docs, insights)

        html = self.env.get_template("report_template.html").render(report=report)
        HTML(string=html).write_pdf(out_path)

        log.info("📄 PDF 저장 완료 → %s", out_path)
        return out_path
