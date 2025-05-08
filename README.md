## ✨ Meeting-Report Pipeline

자동으로 **영문 회의 STT → 한국어 요약 + 액션 아이템 + 문서-통합 분석 → HTML · PDF** 보고서를 만들어 주는 파이프라인입니다.
Google Gemini 1.5 Flash API를 사용해 요약과 분석을 수행하며, 실제 운영 중에는 단일 **Pipeline API**(사내 “허브”)가 모든 입력 데이터를 한 번에 반환합니다. 로컬 테스트를 위해서는 더미 JSON( `data/sample_pipeline.json` )을 사용해 동작을 검증할 수 있습니다.

---

### 🗂️ 폴더 구조

```
report/
├─ docker/                 # 빌드·런타임 Dockerfile, entrypoint
├─ secrets/                # Docker-native 시크릿 (api_key, pipeline_api)
├─ data/                   # STT 텍스트 · 테스트용 sample_pipeline.json
├─ out/                    # HTML / PDF 결과물이 저장되는 위치
├─ config/
│  ├─ logging.yaml         # RichHandler 콘솔 로그 설정
│  └─ settings.py          # Pydantic 설정 & 시크릿 로드
├─ src/
│  ├─ cli.py               # ★ 메인 엔트리 포인트
│  ├─ api_clients/         # PipelineClient · GeminiClient · BaseClient
│  ├─ processors/          # Summary / Action / IntegratedAnalysis / ReportBuilder
│  ├─ models/              # Pydantic Schemas & Enums
│  └─ templates/           # Jinja2 HTML 템플릿 (report_template.html)
└─ requirements.txt
```

---

### ⚙️ 사전 준비

| 항목                   | 설명                                                            |
| -------------------- | ------------------------------------------------------------- |
| **Python 3.11-slim** | Dockerfile 내에서 자동 설치                                          |
| **Google API Key**   | `secrets/api_key` 파일(시크릿) – 40+ 자                             |
| **Pipeline API URL** | `secrets/pipeline_api` 파일 – 예) `https://pipeline.ap.loclx.io` |
| **Docker Desktop**   | `docker compose` 실행용                                          |

> **TIP** 단일 API가 아직 준비되지 않았다면 `data/sample_pipeline.json` 더미를 사용해 자동 fallback 됩니다.

---

### 🚀 빌드 & 실행

```bash
# 1) Docker 이미지 빌드
docker compose build

# 2) 보고서 생성
#    - STT 원문(txt) 를 data/ 로 두고, 출력 PDF 경로 지정
docker compose run --rm reportgen \
    python -m src.cli \
      --stt ./data/meeting_stt.txt \
      --out ./out/report.pdf
```

실행 과정

1. **Pipeline API 호출** → 회의 메타, 목적, 주요 논의, STT 청크+문서 컨텍스트 수신
   `404` 이면 `sample_pipeline.json` 로드
2. **Gemini 요약·액션·통합 분석**(한국어)
3. **ReportSchema** 조립 → Jinja2 `report_template.html` 렌더
4. **WeasyPrint** 로 **PDF + HTML** 저장 (`out/` 폴더)
5. 콘솔 로그는 `config/logging.yaml` 설정에 따라 Rich 포맷으로 출력

---

### 🛠️ 개발자 가이드

| 작업          | 위치 / 설명                                                          |
| ----------- | ---------------------------------------------------------------- |
| **새 모델 연동** | `src/api_clients/` 에 Client 추가 후 프로세서 주입                         |
| **템플릿 수정**  | `src/templates/report_template.html` – Tailwind CDN 포함           |
| **폰트 교체**   | `src/templates/fonts/pretendard.css` 경로 수정 또는 다른 Noto Sans KR 추가 |
| **로그 레벨**   | `config/logging.yaml` `src:` 로거 레벨을 DEBUG/INFO 조정                |

---

### ❓ FAQ

| Q                       | A                                                            |
| ----------------------- | ------------------------------------------------------------ |
| **한글이 PDF에서 안 보여요**     | Pretendard Subset TTF를 템플릿에 임베드하고 `@font-face` 로 선언해 해결했습니다. |
| **Gemini API 호출 실패 시?** | 즉시 RuntimeError 로 중단해 더미 응답을 쓰지 않습니다.                        |
| **Pipeline API가 다운이면?** | `404` 검출 후 `data/sample_pipeline.json` 더미를 자동 로드합니다.         |

---

### © License

사내 PoC 용도로만 사용. 외부 배포 금지.
