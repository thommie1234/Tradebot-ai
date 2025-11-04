"""
AI and OpenAI conversation viewer routes.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import sqlite3
from datetime import datetime, timedelta

router = APIRouter(prefix="/ai", tags=["AI"])

DB_PATH = "/root/optifire/data/optifire.db"


@router.get("/conversations")
async def get_conversations(
    limit: int = 50,
    offset: int = 0,
    purpose: str = None
) -> List[Dict[str, Any]]:
    """
    Get OpenAI conversation history.

    Args:
        limit: Maximum number of conversations to return
        offset: Offset for pagination
        purpose: Filter by purpose (e.g., "News Analysis")

    Returns:
        List of conversations with prompt, response, and metadata
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        cursor = conn.cursor()

        if purpose:
            cursor.execute("""
                SELECT * FROM openai_conversations
                WHERE purpose LIKE ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (f"%{purpose}%", limit, offset))
        else:
            cursor.execute("""
                SELECT * FROM openai_conversations
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

        rows = cursor.fetchall()
        conn.close()

        conversations = []
        for row in rows:
            conversations.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "model": row["model"],
                "purpose": row["purpose"],
                "prompt": row["prompt"],
                "response": row["response"],
                "tokens_used": row["tokens_used"],
                "cost_usd": row["cost_usd"],
                "temperature": row["temperature"],
                "max_tokens": row["max_tokens"]
            })

        return conversations

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: int) -> Dict[str, Any]:
    """Get a specific conversation by ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM openai_conversations
            WHERE id = ?
        """, (conversation_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "model": row["model"],
            "purpose": row["purpose"],
            "prompt": row["prompt"],
            "response": row["response"],
            "tokens_used": row["tokens_used"],
            "cost_usd": row["cost_usd"],
            "temperature": row["temperature"],
            "max_tokens": row["max_tokens"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


@router.get("/conversations/stats")
async def get_conversation_stats() -> Dict[str, Any]:
    """Get statistics about OpenAI usage."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Total conversations
        cursor.execute("SELECT COUNT(*) FROM openai_conversations")
        total_conversations = cursor.fetchone()[0]

        # Total tokens and cost
        cursor.execute("SELECT SUM(tokens_used), SUM(cost_usd) FROM openai_conversations")
        total_tokens, total_cost = cursor.fetchone()

        # Last 24 hours
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute("""
            SELECT COUNT(*), SUM(tokens_used), SUM(cost_usd)
            FROM openai_conversations
            WHERE timestamp >= ?
        """, (yesterday,))
        last_24h_count, last_24h_tokens, last_24h_cost = cursor.fetchone()

        # By purpose
        cursor.execute("""
            SELECT purpose, COUNT(*) as count, SUM(tokens_used) as tokens, SUM(cost_usd) as cost
            FROM openai_conversations
            GROUP BY purpose
            ORDER BY count DESC
        """)
        by_purpose = []
        for row in cursor.fetchall():
            by_purpose.append({
                "purpose": row[0],
                "count": row[1],
                "tokens": row[2],
                "cost_usd": row[3]
            })

        conn.close()

        return {
            "total_conversations": total_conversations or 0,
            "total_tokens": total_tokens or 0,
            "total_cost_usd": total_cost or 0.0,
            "last_24h": {
                "conversations": last_24h_count or 0,
                "tokens": last_24h_tokens or 0,
                "cost_usd": last_24h_cost or 0.0
            },
            "by_purpose": by_purpose
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/conversations/search")
async def search_conversations(
    query: str,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search conversations by keyword in prompt or response.

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        Matching conversations
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM openai_conversations
            WHERE prompt LIKE ? OR response LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))

        rows = cursor.fetchall()
        conn.close()

        conversations = []
        for row in rows:
            conversations.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "model": row["model"],
                "purpose": row["purpose"],
                "prompt": row["prompt"][:200] + "..." if len(row["prompt"]) > 200 else row["prompt"],
                "response": row["response"][:200] + "..." if len(row["response"]) > 200 else row["response"],
                "tokens_used": row["tokens_used"],
                "cost_usd": row["cost_usd"]
            })

        return conversations

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search: {str(e)}")
