
from __future__ import annotations
import requests
from typing import Optional, Tuple, Dict, Any
import os
from dotenv import load_dotenv
load_dotenv()


url = os.getenv("URL", "http://localhost:8000")

class ChatModel:
    def __init__(self) -> None:
        self.api_base_url = url

    def set_api_base_url(self, url: str) -> None:
        self.api_base_url = url

    def chat(self, question: str, confirm_write: bool = False, timeout: int = 30) -> Tuple[bool, str]:
        payload: Dict[str, Any] = {"question": question, "confirm_write": confirm_write}
        try:
            resp = requests.post(f"{self.api_base_url}/chat/ask", json=payload, timeout=timeout)
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(f"HTTP error: {e.response.status_code} - {e.response.text}") from e
        return resp.json()
