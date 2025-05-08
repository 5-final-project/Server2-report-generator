"""
src/cli.py
────────────────────────────────────────────────────────────
⛳  커맨드라인 배치 실행:
    단일 Pipeline API → Gemini → HTML + PDF 보고서 저장
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.service.report_service import generate_report


def _args() -> argparse.Namespace:
    p = argparse.ArgumentParser("Generate meeting report (CLI)")
    p.add_argument("--stt", required=True, help="STT 원문(.txt)")
    p.add_argument("--out", required=True, help="출력 디렉터리")
    p.add_argument("--clusters", type=int, default=5)
    p.add_argument("--topk", type=int, default=5)
    return p.parse_args()


def main() -> None:
    args = _args()

    stt_text = Path(args.stt).read_text(encoding="utf-8")
    out_dir  = Path(args.out).resolve()

    paths = generate_report(
        stt_text=stt_text,
        out_dir=out_dir,
        clusters=args.clusters,
        top_k=args.topk,
    )
    print("✅ HTML :", paths['html'])
    print("✅ PDF  :", paths['pdf'])


if __name__ == "__main__":
    main()
