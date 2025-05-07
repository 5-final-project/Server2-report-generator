"""
STT 파일 유틸리티
────────────────────────────────────────────
입력 형식
    data/meeting.txt      →  그냥 평문 (1줄 = 1문장)
    data/meeting.jsonl    →  {"text": "..."} JSON Lines

두 형식을 모두 지원한다.
"""

import json
from pathlib import Path
from typing import List, Union

# ──────────────────────────────────────────
def load_lines(path: Path) -> List[str]:
    """
    평문(.txt) 또는 JSONL(.jsonl) 파일을 읽어
    'text' 문자열 리스트로 반환한다.
    """
    raw_lines = path.read_text(encoding="utf-8").splitlines()

    # 확장자에 따라 파싱 분기
    if path.suffix.lower() == ".jsonl":
        lines: List[str] = []
        for ln in raw_lines:
            ln = ln.strip()
            if not ln:
                continue
            try:
                obj = json.loads(ln)
                lines.append(obj["text"])
            except (json.JSONDecodeError, KeyError):
                # JSON 파싱 실패 시 그대로 문자열로 간주
                lines.append(ln)
        return lines

    else:  # .txt 등
        return [ln.strip() for ln in raw_lines if ln.strip()]


def split_chunks(
    lines: List[str],
    max_chars: int = 1500,
) -> List[str]:
    """
    문자열 리스트를 max_chars 기준으로 병합해
    한국어/영어 청크 리스트를 반환한다.
    """
    chunks: List[str] = []
    buf: List[str] = []
    size = 0

    for text in lines:
        if size + len(text) > max_chars and buf:
            chunks.append("\n".join(buf))
            buf, size = [], 0
        buf.append(text)
        size += len(text)

    if buf:
        chunks.append("\n".join(buf))
    return chunks
