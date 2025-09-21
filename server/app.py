from fastapi import FastAPI
from read_model.views import router as read_router
from write_model.views import router as write_router

app = FastAPI(title="SmartMarket API")

# Read side (Queries)
app.include_router(read_router, prefix="/query", tags=["query"])

# Write side (Commands)
app.include_router(write_router, prefix="/command", tags=["command"])


