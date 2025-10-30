from fastapi import APIRouter, HTTPException
from .chat_controller import chatController, AskRequest, AskResponse

router = APIRouter()
controller = chatController()


@router.post("/analyze_note")
def analyze_note(note: str):
    try:
        result = controller.analyze_and_respond(note)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        result = controller.ask(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))