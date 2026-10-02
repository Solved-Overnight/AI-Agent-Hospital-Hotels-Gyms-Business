import uuid

from fastapi import APIRouter, HTTPException, Request

from app.agent.agent import agent
from app.api.limiter import limiter
from app.api.schemas import ChatRequest, ChatResponse

from app.values import (
    CLINIC_NAME,
    CLINIC_ADDRESS,
    CLINIC_CONTACT,
)


router = APIRouter()


# The backend system will handle conversation IDs automatically using UUID.
@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
def chat(request: Request, chat_request: ChatRequest):

    thread_id = chat_request.thread_id or str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": chat_request.message,
                    }
                ]
            },
            config=config,
        )

        messages = result["messages"]

        assistant_message = messages[-1]

        return ChatResponse(
            response=assistant_message.content,
            thread_id=thread_id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The AI service could not process your request.",
        ) from exc
    
    