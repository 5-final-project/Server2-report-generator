## ✨ Meeting-Report Pipeline

“영문 STT → 한국어 보고서”를 **단 한 번의 HTTP 요청**으로 끝내는 파이프라인입니다.
Google Gemini 1.5 Flash로 요약·액션·통합 분석을 수행하고, 결과를 **HTML + PDF**로 만들며 FastAPI Swagger( `/docs` )로도 호출할 수 있습니다.

---

### 🗂️ 구조 한눈에 보기

```
report/
├─ docker/                  # Dockerfile · entrypoint.sh
├─ docker-compose.yml
├─ requirements.txt
│
├─ secrets/                 # docker-native secrets
│  ├─ api_key               # Google GenAI API Key
│  ├─ pipeline_api          # 허브 API URL
│  └─ llm_api               # Gemini 모델 URL
│
├─ data/
│  ├─ meeting_stt.txt       # 샘플 STT 원문
│  └─ sample_pipeline.json  # 허브 API 더미 응답 (404 fallback)
│
├─ out/                     # 📄 report.html / report.pdf 출력
│
├─ config/
│  ├─ settings.py           # Pydantic Settings + secrets load
│  └─ logging.yaml          # Rich 콘솔 로그 (root=INFO, src=DEBUG)
│
└─ src/
   ├─ cli.py                # ★ 명령행 단일 실행
   ├─ server/               # FastAPI 앱 (swagger UI)
   │   └─ main.py
   ├─ api_clients/          # BaseClient · PipelineClient · GeminiClient
   ├─ processors/           # Summary / Action / IntegratedAnalysis / ReportBuilder
   ├─ service/              # report_service → CLI·API가 공유
   ├─ models/               # Pydantic Schemas (PipelineRequest, ReportSchema …)
   └─ templates/
       ├─ report_template.html
       └─ fonts/pretendard.css
```

---

### ⚙️ 사전 준비

| 항목                 | 내용                                                                                                        |
| ------------------ | --------------------------------------------------------------------------------------------------------- |
| **Docker Desktop** | `docker compose` 로 빌드/실행                                                                                  |
| **API Key**        | `secrets/api_key` – Google Generative Language API                                                        |
| **허브 API**         | `secrets/pipeline_api` (없을 경우 `sample_pipeline.json` 자동 사용)                                               |
| **Gemini URL**     | `secrets/llm_api` (예 : `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest`) |

---

### 🚀 사용법 1 — CLI

```bash
# 이미지 빌드
docker compose build

# 보고서 생성 (PDF·HTML 동시)
docker compose run --rm reportgen \
  python -m src.cli \
    --stt ./data/meeting_stt.txt \
    --out ./out/report.pdf
```

---

### 🚀 사용법 2 — FastAPI 서버

```bash
# 컨테이너 기동 (포트: 8000)
docker compose up
```

* Swagger UI → [http://localhost:8000/docs](http://localhost:8000/docs)
* **POST `/report-json`**

| 필드              | 타입                          | 설명                     |
| --------------- | --------------------------- | ---------------------- |
| `payload`       | JSON 객체                     | 허브-API 파이프라인 JSON     |

응답 예

```json
{
  "html": "/opt/app/out/report.html",
  "pdf":  "/opt/app/out/report.pdf"
}
```

---

### 🛠️ 개발 Tips

| 작업             | 위치 / 방법                                            |
| -------------- | -------------------------------------------------- |
| **프롬프트·모델 교체** | `processors/*.py` 에서 GeminiClient 호출 부분 수정         |
| **템플릿 커스터마이징** | `src/templates/report_template.html` (Tailwind 사용) |
| **PDF 한글 깨짐**  | Pretendard Subset TTF를 `@font-face` 로 임베드 (이미 적용)  |
| **로그 레벨 조정**   | `config/logging.yaml` – `src:` 로거 DEBUG ↔ INFO     |

---

### 🔄 데이터 흐름

1. **허브 API** `POST /pipeline-run`
   ↳ 회의 메타/목적/인사이트/STT 청크+문서 컨텍스트
   ↳ **404** → `data/sample_pipeline.json` fallback
2. **Gemini API** 3 회 호출

   * 한국어 요약 / 액션 아이템 / 통합 분석
3. **ReportSchema** 조립
4. **Jinja2 → HTML** 렌더
5. **WeasyPrint** 로 PDF 변환 + Pretendard 폰트 임베드
6. 경로 반환 & 로그 출력

---

### © License

사내 PoC 용도. 외부 배포 금지.
