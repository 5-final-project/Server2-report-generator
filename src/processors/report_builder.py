"""
src/processors/report_builder.py
────────────────────────────────────────────────────────────
ReportSchema + 메타 → Jinja2 HTML → WeasyPrint PDF & HTML
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from config.settings import get_settings
from src.models.schemas import ReportSchema, MeetingMeta, SearchDoc

log = logging.getLogger(__name__)


class ReportBuilder:
    def __init__(self) -> None:
        cfg = get_settings()
        self.env = Environment(
            loader=FileSystemLoader(cfg.template_dir),
            autoescape=select_autoescape(),
        )

    # ---------------------------------------------------------------- private
    def _render_html(
        self,
        *,
        report: ReportSchema,
        meta: MeetingMeta,
        purpose: str,
        docs: Iterable[SearchDoc],
    ) -> str:
        """템플릿 → HTML 문자열"""
        return self.env.get_template("report_template.html").render(
            # 템플릿이 요구하는 이름으로 매핑
            meta=meta,
            purpose=purpose,
            agenda=report.agenda_keypoints,
            summary=report.executive_summary,
            actions=report.action_items,
            analysis=report.appendix[0] if report.appendix else "",
            docs=list(docs),
        )

    # ---------------------------------------------------------------- public
    def build_report(
        self,
        *,
        report: ReportSchema,
        meta: MeetingMeta,
        purpose: str,
        docs: Iterable[SearchDoc],
        out_pdf: Path,
        out_html: Optional[Path] = None,
    ) -> None:
        """
        HTML + PDF 동시 생성
        """
        html_str = self._render_html(
            report=report,
            meta=meta,
            purpose=purpose,
            docs=docs,
        )

        out_html = out_html or out_pdf.with_suffix(".html")
        out_html.write_text(html_str, encoding="utf-8")
        log.info("📝 HTML 저장 → %s", out_html)

        HTML(string=html_str, base_url=".").write_pdf(out_pdf)
        log.info("📄 PDF 저장 → %s", out_pdf)
