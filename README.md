# Meeting Report Generator

회의 음성(STT) → 벡터 검색(RAG) → 핵심 인사이트 → **PDF 보고서**를 자동 생성하는 파이프라인.

- 음성 STT 텍스트 변환
- 한국어 번역
- 요약 및 관련 문서 검색
- 핵심 인사이트 정리
- HTML 및 PDF 보고서 생성

모든 프로세스는 로컬 컨테이너 기반으로 작동하며, 별도 서버나 클라우드 의존 없이 내부망에서도 실행 가능하다.

---

## 시스템 구조

```mermaid
graph TD
    A[STT 결과 (txt 또는 jsonl)] -->|청크 분할| B[영어 청크]
    B -->|Qwen 번역| C[한국어 청크]
    C -->|요약 및 문서 검색 - Gemini| D[요약 및 유사 문서]
    C -->|벡터 검색 - Vector DB| E[추가 문서]
    D --> F[관련 문서 집합]
    E --> F
    F -->|Function-call 호출| G[보고서 JSON 생성]
    G -->|Jinja2 템플릿| H[HTML 보고서]
    H -->|WeasyPrint 변환| I[최종 PDF]
```

- Qwen 3-8B GGUF 모델: 번역 및 JSON 보고서 생성 담당 (function-call 기반)
- Gemini 2.5: 문서 요약 및 관련 문서 검색 (Sentence-E5 임베딩 기반)
- LangChain + FAISS: 임베딩 벡터 기반 문서 검색 API
- WeasyPrint: HTML 템플릿 기반 PDF 생성

---

## 디렉토리 구성

```
.
├── data/                  # 입력 STT 파일 (.txt or .jsonl)
├── out/                   # 생성된 PDF 저장 위치
├── secrets/               # API 엔드포인트 설정
│   ├── api_key            # 인증 키 (필요시 사용)
│   ├── chunk_api          # 청크 요약 API 주소
│   ├── vector_api         # 벡터 검색 API 주소
│   └── llm_api            # Qwen API 주소
├── config/
│   ├── settings.py        # 환경변수 설정 (Pydantic 기반)
│   └── logging.yaml       # 로그 출력 설정
├── src/
│   ├── api_clients/       # 외부 API 연동 모듈
│   ├── processors/        # 주요 기능 로직 (번역, 요약, 보고서 생성 등)
│   ├── models/            # 데이터 스키마 정의
│   └── templates/
│       └── report_template.html  # HTML 기반 보고서 템플릿
├── docker/
│   ├── Dockerfile         # Python + WeasyPrint 환경 구성
│   └── entrypoint.sh
├── docker-compose.yml     # 실행 환경 정의
├── requirements.txt       # 패키지 목록
└── README.md
```

---

## 실행 방법

### 1. 저장소 클론
```bash
git clone https://github.com/5-final-project/Server2-report-generator.git
cd Server2-report-generator
```

### 2. 시크릿 설정
```bash
echo "" > secrets/api_key
echo "https://chunk5.ap.loclx.io" > secrets/chunk_api
echo "https://vector.ap.loclx.io" > secrets/vector_api
echo "https://qwen.ap.loclx.io"   > secrets/llm_api
```

### 3. STT 텍스트 파일 준비
```bash
cp my_meeting.txt data/sample_meeting.txt
# 또는 JSONL 형식도 지원
```

### 4. 컨테이너 실행
```bash
docker compose up --build
# 생성된 PDF는 out/report.pdf 에 저장됨
```

### 5. 선택 실행 (명령어로 직접 실행할 경우)
```bash
docker compose run --rm reportgen \
  --stt data/sample_meeting.txt \
  --out out/my_report.pdf
```

---

## 사용 기술 요약

| 목적                 | 기술 스택                              |
|----------------------|-----------------------------------------|
| 번역 및 보고서 생성  | Qwen 3-8B GGUF (function-call 기반)     |
| 요약 및 유사 문서 검색 | Gemini 2.5 Flash + Sentence-E5 임베딩  |
| 벡터 기반 검색        | LangChain + FAISS                      |
| PDF 생성             | Jinja2 템플릿 + WeasyPrint             |
| 컨테이너 환경         | Python 3.11-slim + Docker Compose       |

---

## 참고 사항

- 모든 서비스는 REST API 형태로 연동되며, 구성 요소는 독립적으로 대체 가능함
- 외부 네트워크가 불안정한 경우 로컬 fallback 처리 로직이 포함되어 있음