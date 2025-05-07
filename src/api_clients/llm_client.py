"""
Qwen3-8B /generate 래퍼
────────────────────────────────────────────────────────────
▪ generate()                : 일반 완성
▪ generate_with_tools()     : 함수-호출(funtions/function_call) 완성
"""
from __future__ import annotations

import json
from typing import Optional, Any, Dict, List

from .base import BaseClient


class LLMClient(BaseClient):
    # ────────────── helper
    @staticmethod
    def _msg(role: str, content: str) -> Dict[str, str]:
        return {"role": role, "content": content}

    # ────────────── normal completion
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        top_p: float = 0.9,
    ) -> str:
        body = {
            "messages": [
                self._msg("system", system_prompt),
                self._msg("user", user_prompt),
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        data = self._post("/generate", body)
        return data["text"].strip()

    # ────────────── function-call completion
    def generate_with_tools(
        self,
        schema: Dict[str, Any],
        user_content: str,
        system_prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        body = {
            "messages": [
                self._msg("system", system_prompt),
                self._msg("user", user_content),
            ],
            "functions": [
                {
                    "name": "make_report",
                    "description": "회의 보고서를 JSON 형식으로 생성한다.",
                    "parameters": schema,
                }
            ],
            "function_call": {"name": "make_report"},
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        return self._post("/generate", body)
