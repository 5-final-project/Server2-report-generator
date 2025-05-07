from functools import lru_cache
from pathlib import Path
from pydantic import AnyUrl, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # ───────── 필수 시크릿 ─────────
    CHUNK_API:  AnyUrl
    VECTOR_API: AnyUrl
    LLM_API:    AnyUrl
    API_KEY:    str = Field(..., min_length=10)

    # ───────── 선택 ────────────────
    TEMPLATE_DIR: Path = Field(default=_ROOT / "src" / "templates")

    model_config = SettingsConfigDict(
        secrets_dir="/run/secrets",   # Docker Secrets
        env_file=(".env",),           # 로컬 개발
        extra="ignore",
    )

    @property
    def template_dir(self) -> Path:
        if not self.TEMPLATE_DIR.exists():
            raise FileNotFoundError(self.TEMPLATE_DIR)
        return self.TEMPLATE_DIR


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        import logging, sys
        logging.error("환경 변수/시크릿 검증 실패: %s", e)
        sys.exit(1)
