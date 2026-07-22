import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

load_dotenv()

# --- 1. Library Tools Define Karte Hain ---
@tool
def search_books(query: str) -> str:
    """Search for books in the library inventory by title or genre."""
    # Aap yahan apna database call ya mock data rakh sakti hain
    books = {
        "python": "Python Programming by John Doe (Available: 2 copies)",
        "atomic habits": "Atomic Habits by James Clear (Available: 1 copy)",
        "fastapi": "FastAPI Masterclass by Sarah Lee (Available: 3 copies)"
    }
    query_lower = query.lower()
    for key, val in books.items():
        if key in query_lower:
            return val
    return f"No books found matching '{query}'."

@tool
def borrow_book(book_name: str) -> str:
    """Borrow a book from the library. Limit is 3 books."""
    return f"Success! You have borrowed '{book_name}'. Enjoy reading!"

tools = [search_books, borrow_book]

# --- 2. Model & LangGraph Agent Setup ---
# Agar aap GroqAI use kar rahi hain:
model = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# LangGraph ka ReAct agent create kar rahe hain jo tools ko khud manage karega
agent_executor = create_react_agent(model, tools)

# --- 3. Run & Test the Agent ---
import asyncio

async def main():
    print("🤖 Library Assistant (Powered by LangGraph) is ready!")
    
    # Test query jo library aur tool use karegi
    query = "Can you search for Python books and then help me borrow it?"
    print(f"\nUser: {query}\n")
    
    inputs = {"messages": [("user", query)]}
    
    # LangGraph astream ke zariye steps execute karega
    async for step in agent_executor.astream(inputs, stream_mode="updates"):
        for node_name, node_output in step.items():
            print(f"--- Node: [{node_name}] ---")
            print(node_output)

if __name__ == "__main__":
    asyncio.run(main())