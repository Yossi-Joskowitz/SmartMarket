import requests,json,os
from fastapi import HTTPException
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from common.db import get_conn
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise SystemExit("Missing HF_TOKEN. Set it with: export HF_TOKEN=hf_xxx")

# for sentiment analysis
SENTIMENT_API = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-xlm-roberta-base-sentiment"
INF_HEADERS  = {"Authorization": f"Bearer {HF_TOKEN}"}

# for analyze and respond
CHAT_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "meta-llama/Llama-3.1-8B-Instruct"
CHAT_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}

# for text classification
API_URL_FOR_CLASSIFY = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
HEADERS_FOR_CLASSIFY = {"Authorization": f"Bearer {HF_TOKEN}"}

# for SQL generation
HF_CHAT_API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "meta-llama/Llama-3.1-8B-Instruct"
HEADERS_FOR_CHAT = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
GEN_CFG = {"max_tokens": 500, "temperature": 0.2, "top_p": 0.9}

# for summarizing actions
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}

class AskRequest(BaseModel):
    question: str
    confirm_write: bool = False  

class AskResponse(BaseModel):
    question: str
    field_flags: Dict[str, bool]
    sql: str
    is_write_query: bool
    executed: bool
    rows_affected: Optional[int] = None
    results: Optional[List[Dict[str, Any]]] = None
    message: Optional[str] = None  

@dataclass
class chatModel:
    
    @classmethod
    def get_sentiment(cls, text: str) -> Dict[str, Any]:
        payload = {"inputs": text, "options": {"wait_for_model": True}}
        r = requests.post(SENTIMENT_API, headers=INF_HEADERS, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()[0]
    
    @classmethod
    def analyze_and_respond(cls, text: str , polarity: str) -> str:
        system_msg = "You are a helpful assistant who writes concise, natural English."
        user_msg = f"""
            You analyze what the seller wrote to himself about the product.
            Write a short summary, in natural-sounding English, that reflects the emotion and meaning.
            And maybe a solution in case it requires a solution.
            Write it as if you were the seller.

            Original note: "{text}"
            Detected sentiment: {polarity}

            Constraints:
            - Be brief (one or two sentences).
            - Sound like the seller writing a note to themselves.
            - If sentiment is negative, suggest a practical next step.
            """

        data = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            "max_tokens": 140,
            "temperature": 0.3,
            "top_p": 0.9,
        }

        r = requests.post(CHAT_URL, headers=CHAT_HEADERS, json=data, timeout=60)
        r.raise_for_status()
        out = r.json()["choices"][0]["message"]["content"].strip()
        return out
    

    @classmethod
    def classify(cls, text: str) -> Dict[str, float]:
        data = {
            "inputs": text,
            "parameters": {
                "candidate_labels": ["product_id","name","current_price","cost_price","quantity","brand","category","is_on_promotion","promotion_discount_percent","image_url","note","inventory_value","total_profit","updated_at_utc"],
                "multi_label": True
            },
            "options": {"wait_for_model": True}
        }
        response = requests.post(API_URL_FOR_CLASSIFY, headers=HEADERS_FOR_CLASSIFY, json=data)
        response = response.json()
        if "error" in response:
            raise HTTPException(status_code=500, detail=f"Classification API error: {response['error']}")
        response = dict(zip(response['labels'], response['scores']))
        response = {k: v > 0.5 for k, v in response.items()}
        return response
    
    @classmethod
    def build_sql(cls,question: str, field_flags: dict) -> str:
        schema = """
        TABLE dbo.readProduct(product_id TEXT,name TEXT,current_price FLOAT,cost_price FLOAT,quantity INT,brand TEXT,category TEXT,is_on_promotion BIT,promotion_discount_percent FLOAT,image_url TEXT,note TEXT,inventory_value FLOAT,total_profit FLOAT,updated_at_utc DATETIME)
        """

        prompt = f"""
        You are an expert Text-to-SQL generator. Return **only** valid SQL Server (T-SQL) code without any quotation marks before or after  — no explanations.

        [SCHEMA]
        {schema}

        [QUESTION]
        {question}

        [FIELD FLAGS]
        {json.dumps(field_flags, indent=2)}

        Generate one SQL query matching the intent of the question, using correct filters, sorting, and aggregation.
        Use dbo.readProduct as the table. Return SQL only.
        """

        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            **GEN_CFG,
        }

        r = requests.post(HF_CHAT_API_URL, headers=HEADERS_FOR_CHAT, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


    @classmethod
    def summarize_action(cls, api_response: dict) -> str:
        prompt = f"""
    You are an assistant that summarizes SQL actions in natural English.

    Given the following JSON object that includes:
    - the original question,
    - the SQL query generated,
    - and flags such as whether it is a write query and whether it was executed,

    write **one short, natural English sentence** describing what the system is about to do or has done.

    Rules:
    1. If "is_write_query" is true **and** "executed" is false:
    → Explain what change would happen (e.g., create/update/delete) and end the message by asking for confirmation.
    Example: "You are about to create a new product called 'bread' with barcode 12345 and prices 20→30. Do you want to proceed?"
    2. If "is_write_query" is true **and** "executed" is true:
    → Describe what change was made, in past tense.
    Example: "A new product named 'bread' was created successfully."
    3. If "is_write_query" is false:
    → Summarize what information the query retrieves.
    Example: "You asked to view the most profitable products this month."

    Return only the final English sentence without explanations or markdown.

    JSON:
    {json.dumps(api_response, indent=2)}
    """

        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            **GEN_CFG,
        }
        r = requests.post(HF_CHAT_API_URL, headers=HEADERS, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

    @classmethod
    def _fetch_all_dict(cls,cur) -> List[Dict[str, Any]]:
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
        out = []
        for r in rows:
            if isinstance(r, dict):
                out.append(r)
            else:
                out.append({cols[i]: r[i] for i in range(len(cols))})
        return out

    @classmethod
    def execute_sql(cls, sql: str, req, flags: Dict[str, bool], is_write: bool) -> Dict[str, Any]:
       
        if is_write and not req.confirm_write:
                return AskResponse(
                    question=req.question,
                    field_flags=flags,
                    sql=sql,
                    is_write_query=True,
                    executed=False,
                    message=cls.summarize_action({
                            "question": req.question,
                            "sql": sql,
                            "is_write_query": bool(is_write),
                            "executed": False,
                        })
                )

        with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    if cur.description:
                        results = cls._fetch_all_dict(cur)
                        message = cls.summarize_action({
                            "question": req.question,
                            "sql": sql,
                            "is_write_query": bool(is_write),
                            "executed": True,
                        })
                        return AskResponse(
                            question=req.question,
                            field_flags=flags,
                            sql=sql,
                            is_write_query=is_write,
                            executed=True,
                            results=results,
                            message=message,
                        )
                    else:
                        try:
                            conn.commit()
                        except Exception:
                            pass
                        affected = getattr(cur, "rowcount", None)
                        return AskResponse(
                            question=req.question,
                            field_flags=flags,
                            sql=sql,
                            is_write_query=is_write,
                            executed=True,
                            rows_affected=affected,
                            message=cls.summarize_action({
                                "question": req.question,
                                "sql": sql,
                                "is_write_query": bool(is_write),
                                "executed": True,
                            })
                        )
                
        



