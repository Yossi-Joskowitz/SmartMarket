from fastapi import FastAPI
from fastapi.responses import  RedirectResponse, Response
from readFrom.read_view import router as read_router
from writeTo.write_view import router as write_router
from chat.chat_view import router as chat_router


app = FastAPI(title="SmartMarket API")

# Read side (Queries)
app.include_router(read_router, prefix="/query", tags=["query"])

# Write side (Commands)
app.include_router(write_router, prefix="/command", tags=["command"])

# chat
app.include_router(chat_router, prefix="/chat", tags=["chat"])


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}

@app.head("/", include_in_schema=False)
def head_root():
    return Response(status_code=200)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

