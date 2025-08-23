from fastapi import APIRouter, Request, Form
from fastapi.responses import StreamingResponse, JSONResponse
from backend.auth import get_current_user
from backend.azure_openai_utils import stream_chat_with_documents

router = APIRouter()


@router.post("/chat/stream")
async def chat_stream(
    request: Request,
    query: str = Form(...),
    selected_file: str = Form(None)
):
    user_id = get_current_user(request)
    session_id = request.cookies.get("session_id")

    # Namespace logic
    if user_id:
        namespace = f"user_{user_id}"
    elif session_id:
        namespace = f"session_{session_id}"
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing session or user authentication."}
        )

    try:
        # Streaming response from RAG (OpenAI + Pinecone)
        async def generator():
            async for chunk in stream_chat_with_documents(query, namespace, selected_file):
                yield chunk

        return StreamingResponse(generator(), media_type="text/plain")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
