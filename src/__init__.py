"""
패키지 초기화: 로깅 설정 적용
"""
import logging.config
from pathlib import Path
import yaml

_LOG_CFG = Path(__file__).resolve().parent.parent / "config" / "logging.yaml"

with _LOG_CFG.open("r", encoding="utf-8") as fh:
    logging.config.dictConfig(yaml.safe_load(fh))
