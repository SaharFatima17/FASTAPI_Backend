from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import os
import asyncio
from groq import AsyncGroq
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.database import get_db
from app.models import ChatSession, ChatMessage

load_dotenv()

router = APIRouter(prefix="/chat", tags=["Chat"])

# Groq Client Initialize
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# 1. Moderation Check Function
async def check_moderation(text: str) -> bool:
    """
    User input ko check karta hai ke wo safe hai ya nahi.
    Groq ya kisi bhi lightweight model se moderation check karwaya ja sakta hai.
    DUMMY SAFEGUARD: Aap real production mein OpenAI Moderation API ya HuggingFace use kar sakte hain.
    Hum yahan check kar rahe hain ke agar content harmful keywords contain karta hai toh block karein.
    """
    harmful_keywords = ["how to make a bomb", "hack", "illegal", "self-harm"]
    for word in harmful_keywords:
        if word in text.lower():
            return False  # Moderation failed
    return True  # Safe

# 2. Retry with Exponential Backoff decorator
# Rate limit (429) aur Timeout errors par retry karega.
# Pehla try fail hone par 2s wait karega, phir 4s, phir 8s... maximum 3 attempts tak.
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    retry=retry_if_exception_type(Exception),  # Production mein specific Groq API Errors par filter karein
    reraise=True
)
async def call_groq_with_retry(messages, model="llama-3.3-70b-versatile"):
    """Groq API call with built-in retry mechanisms."""
    return await groq_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=500,
        stream=True
    )

@router.get("/stream")
async def chat_stream_endpoint(
    message: str = Query(..., description="User's input message"),
    session_key: str = Query("default_session"),
    db: Session = Depends(get_db)
):
    # 1. Moderation Check
    is_safe = await check_moderation(message)
    if not is_safe:
        return StreamingResponse(
            (f"data: {json.dumps({'error': 'Your message violated our safety guidelines. Request blocked.'})}\n\n" for _ in range(1)),
            media_type="text/event-stream"
        )

    # 2. Database Session check/create
    chat_session = db.query(ChatSession).filter(ChatSession.session_key == session_key).first()
    if not chat_session:
        chat_session = ChatSession(session_key=session_key)
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)

    # 3. User Message Save
    user_msg = ChatMessage(session_id=chat_session.id, sender="user", content=message)
    db.add(user_msg)
    db.commit()

    async def event_generator():
        full_reply = ""
        try:
            # 4. Call API with Retry wrapper
            messages = [
                {"role": "system", "content": "You are Zylo Core, a helpful and professional enterprise AI assistant."},
                {"role": "user", "content": message}
            ]
            
            response = await call_groq_with_retry(messages)

            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    token_text = chunk.choices[0].delta.content
                    full_reply += token_text
                    yield f"data: {json.dumps({'token': token_text})}\n\n"

            # 5. DB mein complete response save karein
            assistant_msg = ChatMessage(session_id=chat_session.id, sender="assistant", content=full_reply.strip())
            db.add(assistant_msg)
            db.commit()

            print("\n" + "="*50)
            print("📊 GROQ API USAGE STATS (With Retry & Moderation)")
            print(f"🔹 Session Key:       {session_key}")
            print(f"🔹 Model:             Llama 3.3 70B (Groq)")
            print("="*50 + "\n")

        except Exception as e:
            print(f"❌ Failed after retries. Error: {str(e)}")
            yield f"data: {json.dumps({'error': 'System is currently busy. Please try again in a moment.'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")