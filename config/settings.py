from functools import lru_cache
from pathlib import Path

from pydantic import AnyUrl, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # ───────── 필수 시크릿 ─────────
    PIPELINE_API: AnyUrl               # 단일 허브(파이프라인) API
    LLM_API:      AnyUrl               # LLM 엔드포인트(Gemini·Claude·Qwen 등)
    API_KEY:      str = Field(min_length=10)

    # ───────── 선택 ────────────────
    TEMPLATE_DIR: Path = Field(default=_ROOT / "src" / "templates")

    # ───────── Pydantic 설정 ────────
    model_config = SettingsConfigDict(
        secrets_dir="/run/secrets",   # Docker Secrets 마운트 경로
        env_file=(".env",),           # 로컬 개발용 .env
        extra="ignore",
    )

    # 템플릿 디렉터리 유효성 확인
    @property
    def template_dir(self) -> Path:
        if not self.TEMPLATE_DIR.exists():
            raise FileNotFoundError(self.TEMPLATE_DIR)
        return self.TEMPLATE_DIR


# 싱글턴 캐시
@lru_cache
def get_settings() -> "Settings":
    try:
        return Settings()
    except ValidationError as e:
        import logging, sys
        logging.error("환경 변수/시크릿 검증 실패: %s", e)
        sys.exit(1)
