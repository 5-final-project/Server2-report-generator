# Meeting Report Generator

회의 음성(STT) → 벡터 검색(RAG) → 핵심 인사이트 → **PDF 보고서**를 자동 생성하는 파이프라인.

## 실행

```bash
# Docker (Secrets 사용)
docker compose up --build

# 로컬 가상환경
export CHUNK_API="https://chunk5.ap.loclx.io"
export VECTOR_API="https://vector.ap.loclx.io"
export LLM_API="https://qwen.ap.loclx.io"
export API_KEY="<TOKEN>"

python -m src.cli --stt data/sample_meeting.jsonl --out out/report.pdf
```

config/      ← 설정·로깅
src/         ← 어플리케이션 모듈
data/        ← STT 입력 예시
out/         ← PDF 출력