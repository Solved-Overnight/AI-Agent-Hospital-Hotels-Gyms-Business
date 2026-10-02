from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    thread_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    thread_id: str