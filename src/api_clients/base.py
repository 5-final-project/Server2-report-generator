"""
src/api_clients/base.py
────────────────────────────────────────────────────────────
· 각 REST 클라이언트가 httpx.Client 하나씩 보유
· add_auth      → Authorization 헤더 추가 여부
· extra_headers → 서비스 전용 헤더(dict) 주입
"""
from __future__ import annotations

import httpx
from typing import Any, Final, Dict, Union
from pydantic import AnyUrl

from config.settings import get_settings

_settings = get_settings()
_TIMEOUT: Final = httpx.Timeout(180.0, connect=10.0)


def _build_session(add_auth: bool, extra_headers: Dict[str, str] | None) -> httpx.Client:
    headers = extra_headers.copy() if extra_headers else {}
    if add_auth:
        # 모든 내부 서비스가 Google-Gemini Key 로 인증
        headers["Authorization"] = f"Bearer {_settings.API_KEY}"
    return httpx.Client(timeout=_TIMEOUT, headers=headers)


class BaseClient:
    def __init__(
        self,
        base_url: Union[str, AnyUrl],
        *,
        add_auth: bool = True,
        extra_headers: Dict[str, str] | None = None,
    ) -> None:
        self.base_url = str(base_url).rstrip("/")
        self.session = _build_session(add_auth, extra_headers)

    # --------------------------------------------------
    def _post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = self.session.post(url, json=json)
        resp.raise_for_status()
        return resp.json()
