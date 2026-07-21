import json
import os
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from groq import AsyncGroq
from dotenv import load_dotenv

from app.core.database import get_db
from app.models import ChatSession, ChatMessage
from app.services.library_tools import (
    search_books, check_availability, borrow_book, 
    return_book, get_my_borrowed_books
)

load_dotenv()
router = APIRouter(prefix="/chat", tags=["Chat"])
groq_client = AsyncGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    timeout=60.0
)

# --- 1. TOOLS DEFINITION ---
tools = [
    {"type": "function", "function": {"name": "search_books", "description": "Search for books in the local library inventory by title or author.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "check_availability", "description": "Check if a book is available in the local library by ID.", "parameters": {"type": "object", "properties": {"book_id": {"type": "integer"}}, "required": ["book_id"]}}},
    {"type": "function", "function": {"name": "borrow_book", "description": "Borrow a book from the local library by ID (Limit: 3).", "parameters": {"type": "object", "properties": {"book_id": {"type": "integer"}}, "required": ["book_id"]}}},
    {"type": "function", "function": {"name": "return_book", "description": "Return a borrowed book to the local library by ID.", "parameters": {"type": "object", "properties": {"book_id": {"type": "integer"}}, "required": ["book_id"]}}},
    {"type": "function", "function": {"name": "get_my_borrowed_books", "description": "View books I have currently borrowed from the library.", "parameters": {"type": "object", "properties": {}}}}
]

# --- 2. DATABASE LOGIC ---
def handle_database_action(tool_name, arguments, db, user_id=1):
    try:
        args = json.loads(arguments) if arguments else {}
        
        if tool_name == "search_books":
            results = search_books(db, args.get("query", ""))
            return "Here are the books found in the local library inventory: " + ", ".join([f"'{b['title']}' (ID: {b['id']}, Author: {b['author']}, Available: {b['available']})" for b in results]) if results else "No books found matching that query in the library."
        
        elif tool_name == "check_availability":
            res = check_availability(db, int(args.get("book_id", 0)))
            if isinstance(res, str): return res
            return f"'{res['title']}' is currently available. {res['available']} out of {res['total']} copies are ready for you."
            
        elif tool_name == "borrow_book":
            return borrow_book(db, user_id, int(args.get("book_id", 0)))["reason"]
            
        elif tool_name == "return_book":
            return return_book(db, user_id, int(args.get("book_id", 0)))["reason"]
            
        elif tool_name == "get_my_borrowed_books":
            loans = get_my_borrowed_books(db, user_id)
            if not loans: return "You don't have any books currently borrowed."
            return "You currently have these books: " + ", ".join([f"Book ID {l['book_id']} (Due: {l['due_date']})" for l in loans])
        
        return "I'm sorry, I encountered an unknown action."
    except Exception as e:
        return f"I apologize, I had trouble processing that action. Error: {str(e)}"


# --- 3. STREAMING ENDPOINT ---
@router.get("/stream")
async def chat_stream_endpoint(message: str = Query(...), session_key: str = Query("default"), db: Session = Depends(get_db)):
    
    async def event_generator():
        full_reply = ""
        system_instructions = """You are Zylo, a professional, friendly, and helpful Library Assistant.
        - STRICT INVENTORY RULES:
          1. Whenever the user asks to search, check availability, or borrow/return a book by name or general description, you MUST ALWAYS call the appropriate tool ('search_books', 'check_availability', 'borrow_book') using the database tools.
          2. If the user wants to borrow a book by name (e.g. 'Python programming book'), ALWAYS call 'search_books' first to find its ID, and then use that ID to call 'borrow_book'. Never guess or claim a book isn't in inventory without searching first.
        - HYBRID CAPABILITY: For general world knowledge questions completely unrelated to the library inventory, use your global knowledge base directly.
        - Respond in a natural, conversational tone.
        - NEVER use tags like [System], [Error], or similar labels. Keep it clean."""
        
        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": message}
        ]
        
        try:
            # First call non-streaming to safely catch tool calls if triggered
            response = await groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=messages, 
                tools=tools, 
                tool_choice="auto", 
                stream=False
            )
            
            message_obj = response.choices[0].message
            
            if message_obj.tool_calls:
                tool_call = message_obj.tool_calls[0]
                tool_call_id = tool_call.id
                tool_function_name = tool_call.function.name
                tool_arguments_str = tool_call.function.arguments
                
                # Execute database action
                db_result = handle_database_action(tool_function_name, tool_arguments_str, db)
                
                messages.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tool_call_id,
                            "type": "function",
                            "function": {
                                "name": tool_function_name,
                                "arguments": tool_arguments_str
                            }
                        }
                    ]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": str(db_result)
                })

                # Second call to get final conversational response based on tool results
                second_response = await groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile", 
                    messages=messages,
                    stream=False
                )
                
                final_text = second_response.choices[0].message.content
                if final_text:
                    yield f"data: {json.dumps({'token': final_text})}\n\n"
                    full_reply += final_text
            else:
                final_text = message_obj.content
                if final_text:
                    yield f"data: {json.dumps({'token': final_text})}\n\n"
                    full_reply += final_text

        except Exception as e:
            error_msg = f"I am having trouble processing your request right now."
            yield f"data: {json.dumps({'token': error_msg})}\n\n"
            full_reply += error_msg

        # Save to database session (Auto-create session if it doesn't exist to prevent history loss on refresh)
        session = db.query(ChatSession).filter(ChatSession.session_key == session_key).first()
        if not session:
            session = ChatSession(session_key=session_key)
            db.add(session)
            db.commit()
            db.refresh(session)
            
        if session:
            db.add(ChatMessage(session_id=session.id, sender="user", content=message))
            db.add(ChatMessage(session_id=session.id, sender="assistant", content=full_reply))
            db.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from fastapi import Query

@router.get("/history")
async def get_chat_history(session_key: str = Query("default"), db: Session = Depends(get_db)):
    # Session find karein ya create karein
    session = db.query(ChatSession).filter(ChatSession.session_key == session_key).first()
    if not session:
        return []
    
    # Messages fetch karein
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc()).all()
    return [{"sender": m.sender, "content": m.content} for m in messages]