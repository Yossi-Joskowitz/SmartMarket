from .chat_model import chatModel, AskResponse, AskRequest
from fastapi import HTTPException
import re



TWO_WORD_TAG = {"negative": "Not good","neutral":  "Needs check","positive": "All good",}

WRITE_RE = re.compile(r"^(insert|update|delete|merge|alter|drop|truncate|create|exec|grant|revoke)\b", re.I)

class chatController:

    def get_sentiment(self,text: str):
        preds = chatModel.get_sentiment(text)
        label_map = {"LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"}

        # normalize scores to percentages
        total = sum(p["score"] for p in preds)
        scores = {label_map.get(p["label"], p["label"]).lower(): round(p["score"] / total * 100, 2) for p in preds}

        best_label = max(scores, key=scores.get)
        return best_label, scores

    def analyze_and_respond(self, text: str):
        polarity, scores = self.get_sentiment(text)
        tag = TWO_WORD_TAG.get(polarity, "Needs check")

        out = chatModel.analyze_and_respond(text,polarity)
        
        return {
            "sentiment_breakdown": scores,
            "tag": tag,
            "summary": out,
        }
    
    def classify(self,text: str):
       return chatModel.classify(text)

    def build_sql(self, question: str, field_flags: dict) -> str:
        return chatModel.build_sql(question, field_flags)

    def summarize_action(self, api_response: dict) -> str:
        return chatModel.summarize_action(api_response)

    def _is_write_query(self, sql: str) -> bool:
        return bool(WRITE_RE.match(sql.strip()))

    def ask(self, req: AskRequest) -> AskResponse:
        try:
            try:
                flags = self.classify(req.question)
            except HTTPException as he:
                raise he

            try:
                sql = self.build_sql(req.question, flags)
            except Exception as e:
                raise RuntimeError(f"SQL generation error: {e}")

            is_write = self._is_write_query(sql)

            
            return chatModel.execute_sql(sql, req, flags, is_write)
            

        except HTTPException as e:
            raise HTTPException(status_code=500, detail=str(e))


    #######################################################################







