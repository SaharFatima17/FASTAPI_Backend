from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ChatSession, ChatMessage
from app.api.v1.agents import orchestrator_router  # 👈 Orchestrator import kiya gaya hai

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws/echo")
async def websocket_echo_endpoint(
    websocket: WebSocket, 
    session_key: str = Query("default_session"),
    db: Session = Depends(get_db)
):
    await websocket.accept()
    print(f"⚡ WebSocket Tunnel Opened for Session: {session_key}")

    # Database mein session check karein, nahi toh naya banayein
    chat_session = db.query(ChatSession).filter(ChatSession.session_key == session_key).first()
    if not chat_session:
        chat_session = ChatSession(session_key=session_key)
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        print(f"🆕 Created New Chat Session in DB: {session_key}")
    else:
        print(f"📚 Found Existing Session '{session_key}'. Rebuilding history...")
        history = db.query(ChatMessage).filter(ChatMessage.session_id == chat_session.id).order_by(ChatMessage.timestamp.asc()).all()
        for msg in history:
            await websocket.send_json({
                "sender": msg.sender,
                "content": msg.content,
                "is_history": True
            })

    try:
        while True:
            raw_data = await websocket.receive_text()
            print(f"📥 Received: {raw_data}")

            # 1. User message database mein save karein
            user_msg = ChatMessage(session_id=chat_session.id, sender="user", content=raw_data)
            db.add(user_msg)
            db.commit()

            # 2. Server Echo ki jagah Orchestrator Agent use karein (with Max-Hop Guardrail)
            assistant_reply = orchestrator_router(query=raw_data, session_key=session_key, max_hops=3)

            # 3. Assistant message database mein save karein
            assistant_msg = ChatMessage(session_id=chat_session.id, sender="assistant", content=assistant_reply)
            db.add(assistant_msg)
            db.commit()

            # 4. Client ko response bhejein
            await websocket.send_json({
                "sender": "assistant",
                "content": assistant_reply
            })
            print("💾 Saved both user and assistant messages to PostgreSQL via Orchestrator!")

    except WebSocketDisconnect:
        print(f"❌ Session '{session_key}' disconnected.")