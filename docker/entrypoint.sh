#!/usr/bin/env bash
set -euo pipefail

# ────────────────────────── 시크릿 → ENV ──────────────────────────
for secret in /run/secrets/*; do
  key=$(basename "$secret")
  export "$key"="$(cat "$secret")"
done

# ────────────────────────── 기본 인자 설정 ────────────────────────
ARGS=${@:-"--stt data/sample_meeting.txt --out out/report.pdf"}

# ────────────────────────── 파이프라인 실행 ──────────────────────
python -m src.cli ${ARGS}
