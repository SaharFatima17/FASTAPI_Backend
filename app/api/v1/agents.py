# app/api/v1/agents.py
from typing import List, Dict, Any

# --- 1. CATALOG SPECIALIST AGENT ---
def call_catalog_agent(query: str, session_key: str) -> str:
    """
    Handles operations related to book inventory: search_books, check_availability, 
    borrow_book, return_book, get_my_borrowed_books.
    """
    q = query.lower()
    if "borrow" in q or "get" in q:
        return f"[Catalog Agent]: Processed borrowing/inventory request for session '{session_key}'."
    elif "return" in q:
        return f"[Catalog Agent]: Processed book return for session '{session_key}'."
    else:
        return f"[Catalog Agent]: Searched catalog for query: '{query}'."

# --- 2. POLICY SPECIALIST AGENT ---
def call_policy_agent(query: str) -> str:
    """
    Handles library rules, guidelines, limits, and knowledge base search.
    """
    return f"[Policy Agent]: Searched knowledge base for policy regarding: '{query}'."

# --- 3. ORCHESTRATOR AGENT WITH MAX-HOP GUARDRAIL ---
def orchestrator_router(query: str, session_key: str, max_hops: int = 3) -> str:
    """
    Routing engine: Analyzes the query, routes to appropriate specialists, 
    and enforces a max-hop guardrail to prevent infinite loops.
    """
    hops = 0
    q = query.lower()
    
    # Check if mixed query needs both
    needs_catalog = any(word in q for word in ["borrow", "book", "return", "search", "list", "available"])
    needs_policy = any(word in q for word in ["rule", "limit", "policy", "fine", "allowed", "maximum"])

    response_parts = []

    # Hop 1: Catalog Check
    if needs_catalog or (not needs_policy):
        if hops >= max_hops:
            return "Error: Max-hop guardrail triggered. Routing loop terminated."
        hops += 1
        response_parts.append(call_catalog_agent(query, session_key))

    # Hop 2: Policy Check (if mixed or explicitly policy-related)
    if needs_policy:
        if hops >= max_hops:
            return "Error: Max-hop guardrail triggered. Routing loop terminated."
        hops += 1
        response_parts.append(call_policy_agent(query))

    if not response_parts:
        hops += 1
        response_parts.append(call_catalog_agent(query, session_key))

    return " | ".join(response_parts)