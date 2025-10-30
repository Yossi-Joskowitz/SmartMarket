# tests.py
# NOTE: This script routes user questions to either:
# - a database (SQL Server) to fetch Events rows, then composes an answer with that context
# - or directly to a Hugging Face Inference Router chat model
# It also includes a small "decider" LLM that picks whether we need DB data.

import os
import json
import re
import requests
from typing import List, Dict, Any, Optional, Tuple
from common.db import get_conn
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# ---- DB helpers ----
# NOTE: get_conn() should return a context-managed pyodbc connection to your SQL Server.


def fetch_events_all(max_rows: Optional[int] = 1000) -> List[Dict[str, Any]]:
    """
    Pull rows from dbo.Events (Id, AggregateId, EventType, EventData, CreatedAt).
    - max_rows: if a positive int, limits the number of rows with TOP (...)
    - returns a list of dicts with JSON-decoded EventData when possible
    """
    # NOTE: Build SQL with optional TOP to avoid fetching too many rows
    sql = "SELECT Id, AggregateId, EventType, EventData, CreatedAt FROM dbo.Events ORDER BY Id ASC"
    if isinstance(max_rows, int) and max_rows > 0:
        sql = f"SELECT TOP ({max_rows}) Id, AggregateId, EventType, EventData, CreatedAt FROM dbo.Events ORDER BY Id ASC"

    # NOTE: Execute query
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

    # NOTE: Normalize rows to dictionaries and parse EventData as JSON when it’s a string
    out: List[Dict[str, Any]] = []
    for r in rows:
        try:
            data = json.loads(r.EventData) if isinstance(r.EventData, str) else r.EventData
        except Exception:
            data = r.EventData
        out.append({
            "Id": getattr(r, "Id", None),
            "AggregateId": getattr(r, "AggregateId", None),
            "EventType": getattr(r, "EventType", None),
            "EventData": data,
            "CreatedAt": getattr(r, "CreatedAt", None),
        })
    return out


# ---- Hugging Face Router config ----
# NOTE: Do NOT hardcode tokens. Set an environment variable instead:
# export HF_TOKEN=hf_xxx
HF_TOKEN = "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"
if not HF_TOKEN:
    raise SystemExit("Missing HF_TOKEN. Set it with: export HF_TOKEN=hf_xxx")

# NOTE: HF Inference Router endpoint for chat completions
URL = "https://router.huggingface.co/v1/chat/completions"

# NOTE: Default model can be overridden via env var HF_MODEL
MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")

# NOTE: Standard headers with Bearer auth
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}

# NOTE: Generation config passed to the chat API
GEN_CFG = {"max_tokens": 600, "temperature": 0.2, "top_p": 0.9}

# ---- System prompts ----
# NOTE: High-level chat instruction for regular back-and-forth
SYSTEM_PROMPT_CHAT = (
    "You are a helpful assistant. Reply in English. Keep responses concise and maintain context across turns."
)

# NOTE: A strict decider prompt: returns JSON telling us to query DB or not
DECISION_SYSTEM_PROMPT = (
    "You are a routing assistant. Output ONLY a single JSON object with keys:\n"
    '{"action":"DB_QUERY" or "NO_DB","reason":"short"}\n'
    "- If the user asks about product data, prices, sales, events, promotions, or any fact likely stored in a database → action=DB_QUERY.\n"
    "- Otherwise → action=NO_DB.\n"
    "Return STRICT JSON. No extra text."
)

# NOTE: Answer writer prompt; uses DB context if provided
ANSWER_SYSTEM_PROMPT = (
    "You are a retail analyst. Write a clear, friendly, concise answer in English.\n"
    "Base factual claims ONLY on the provided DB data (if any). If data is missing or insufficient, say so briefly.\n"
    "Use 1–3 short paragraphs and, if helpful, up to 3 bullet points with recommendations."
)


def chat_once(messages: List[Dict[str, str]]) -> Tuple[Optional[str], Optional[str]]:
    """
    Call the HF Router chat API once with a list of messages.
    - returns (content, None) on success or (None, error_message) on failure
    """
    payload = {"model": MODEL, "messages": messages, **GEN_CFG}

    # NOTE: Make HTTP request with timeout
    try:
        resp = requests.post(URL, headers=HEADERS, json=payload, timeout=120)
    except requests.RequestException as e:
        return None, f"Network error: {e}"

    # NOTE: Try to parse JSON body; if not JSON, return raw text
    try:
        data = resp.json()
    except ValueError:
        return None, f"Response not valid JSON:\n{resp.text}"

    # NOTE: Handle non-2xx status codes and surface HF error payload
    if not resp.ok:
        err = data.get("error") or data
        return None, f"API error ({resp.status_code}): {json.dumps(err, ensure_ascii=False)}"

    # NOTE: Extract assistant content safely
    try:
        return data["choices"][0]["message"]["content"].strip(), None
    except (KeyError, IndexError, TypeError):
        return None, f"Unexpected response:\n{json.dumps(data, ensure_ascii=False, indent=2)}"


def decide_need_db(question: str) -> Dict[str, str]:
    """
    Ask the decider model whether we need DB data for this question.
    - returns dict like {"action": "DB_QUERY"|"NO_DB", "reason": "..."}
    """
    messages = [
        {"role": "system", "content": DECISION_SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    # NOTE: Get decider output text or error
    text, err = chat_once(messages)
    if err:
        return {"action": "NO_DB", "reason": f"decider error: {err}"}

    # NOTE: Parse strict JSON; if the model added extra text, try to salvage JSON substring
    try:
        obj = json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not m:
            return {"action": "NO_DB", "reason": "decider returned non-JSON"}
        try:
            obj = json.loads(m.group(0))
        except Exception:
            return {"action": "NO_DB", "reason": "decider JSON parse error"}

    # NOTE: Normalize action; default to NO_DB if unexpected
    action = obj.get("action", "NO_DB")
    if action not in ("DB_QUERY", "NO_DB"):
        action = "NO_DB"
    reason = obj.get("reason", "")
    return {"action": action, "reason": reason}


def answer_with_or_without_db(question: str, db_rows: Optional[List[Dict[str, Any]]]) -> str:
    """
    Compose an answer using DB rows if available; otherwise answer without DB context.
    """
    # NOTE: Limit how many rows we pass to the model to keep prompts small
    context = "No DB data provided."
    if db_rows is not None:
        preview = db_rows[:200]
        context = "DB rows (sample):\n" + json.dumps(preview, ensure_ascii=False, default=str)

    messages = [
        {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
        {"role": "user", "content": f"Question:\n{question}\n\nDB context:\n{context}\n\nFinal answer:"},
    ]

    # NOTE: Generate final answer
    text, err = chat_once(messages)
    if err:
        return f"⚠️ Error generating answer: {err}"
    return text


# from typing import Optional, Dict, Any, List

def chat_answer(question: str, max_rows: int = 1000, force_mode: Optional[str] = None) -> Dict[str, Any]:
    """
    Public function you can import elsewhere (e.g., from a FastAPI router).
    Returns a dict: {"answer": str, "mode": "DB_QUERY"|"NO_DB", "rows_used": int|None}
    """
    # decide mode
    if force_mode == "db":
        mode = "DB_QUERY"
    elif force_mode == "nodb":
        mode = "NO_DB"
    else:
        decision = decide_need_db(question)
        mode = decision.get("action", "NO_DB")

    # answer
    if mode == "DB_QUERY":
        rows: List[Dict[str, Any]] = fetch_events_all(max_rows or 1000)
        answer = answer_with_or_without_db(question, rows)
        return {"answer": answer, "mode": "DB_QUERY", "rows_used": len(rows)}
    else:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_CHAT},
            {"role": "user", "content": question},
        ]
        reply, err = chat_once(messages)
        if err:
            raise RuntimeError(f"Chat error: {err}")
        return {"answer": reply, "mode": "NO_DB", "rows_used": None}





router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    max_rows: Optional[int] = 1000
    force_mode: Optional[str] = None  # "db" | "nodb" | None

class ChatResponse(BaseModel):
    answer: str
    mode: str
    rows_used: Optional[int] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    FastAPI endpoint to ask a question and get an answer (with or without DB).
    """
    try:
        result = chat_answer(req.question, req.max_rows or 1000, req.force_mode)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
