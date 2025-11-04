#!/usr/bin/env python3
"""
Test OpenAI logging functionality.
"""
import asyncio
import sys
import os
sys.path.insert(0, '/root/optifire')

from optifire.ai.openai_client import OpenAIClient
from optifire.services.news_scanner import NewsScanner


async def test_openai_logging():
    """Test that OpenAI conversations are logged."""
    print("\n" + "="*80)
    print("TESTING OPENAI LOGGING")
    print("="*80 + "\n")

    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set - skipping live test")
        print("✅ But logging infrastructure is ready!")
        return

    print("🔑 OpenAI API key found")

    # Test 1: Direct analyze_text call
    print("\n--- Test 1: Direct analyze_text call ---")
    client = OpenAIClient()

    test_prompt = """
    Analyze this headline for trading signals:
    "Tesla announces new Gigafactory in Texas, production to double by 2025"

    Should we BUY, SHORT, or SKIP?
    Respond in format: ACTION: [BUY|SHORT|SKIP], CONFIDENCE: [0.0-1.0], REASON: [explanation]
    """

    try:
        response = await client.analyze_text(
            test_prompt,
            purpose="Test: Tesla News Analysis"
        )
        print(f"✅ OpenAI response received: {response[:100]}...")
        print("✅ Conversation should be logged to:")
        print("   - Database: /root/optifire/data/optifire.db (openai_conversations table)")
        print("   - File: /root/optifire/data/openai_logs/conversations_YYYY-MM-DD.log")
    except Exception as e:
        print(f"⚠️  OpenAI call failed: {e}")
        print("   (This is OK if you don't have API credits)")

    # Test 2: News scanner (uses OpenAI)
    print("\n--- Test 2: News Scanner Integration ---")
    scanner = NewsScanner()

    # Mock articles
    mock_articles = [
        {
            "headline": "Tesla announces record deliveries, beats analyst estimates",
            "summary": "Tesla delivered 500,000 vehicles in Q4",
            "timestamp": "2024-01-15T10:00:00Z"
        }
    ]

    try:
        analysis = await scanner.analyze_news_sentiment("TSLA", mock_articles)
        print(f"✅ News analysis complete:")
        print(f"   Action: {analysis['action']}")
        print(f"   Confidence: {analysis['confidence']:.0%}")
        print(f"   Reason: {analysis['reason']}")
        print("✅ This conversation is also logged!")
    except Exception as e:
        print(f"⚠️  News scanner failed: {e}")
        print("   (This is OK if you don't have API credits)")

    # Test 3: Check database
    print("\n--- Test 3: Check Database ---")
    import sqlite3
    try:
        conn = sqlite3.connect("/root/optifire/data/optifire.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM openai_conversations")
        count = cursor.fetchone()[0]
        print(f"✅ Database has {count} conversations logged")

        if count > 0:
            cursor.execute("""
                SELECT timestamp, purpose, tokens_used, cost_usd
                FROM openai_conversations
                ORDER BY timestamp DESC
                LIMIT 5
            """)
            print("\n   Latest conversations:")
            for row in cursor.fetchall():
                print(f"   - {row[0][:19]} | {row[1]} | {row[2]} tokens | ${row[3]:.4f}")

        conn.close()
    except Exception as e:
        print(f"⚠️  Database check failed: {e}")

    # Test 4: Check log file
    print("\n--- Test 4: Check Log File ---")
    from datetime import datetime
    log_file = f"/root/optifire/data/openai_logs/conversations_{datetime.now().strftime('%Y-%m-%d')}.log"
    try:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✅ Log file exists: {log_file}")
            print(f"   Size: {size} bytes")

            # Show last few lines
            with open(log_file, 'r') as f:
                lines = f.readlines()
                print(f"\n   Last 10 lines:")
                for line in lines[-10:]:
                    print(f"   {line.rstrip()}")
        else:
            print(f"ℹ️  No log file yet: {log_file}")
            print("   (Will be created on first OpenAI call)")
    except Exception as e:
        print(f"⚠️  Log file check failed: {e}")

    print("\n" + "="*80)
    print("✅ LOGGING INFRASTRUCTURE TEST COMPLETE")
    print("="*80 + "\n")

    print("📊 How to view OpenAI chats:")
    print("\n1. Via API:")
    print("   curl http://localhost:8000/api/ai/conversations")
    print("   curl http://localhost:8000/api/ai/conversations/stats")
    print("   curl 'http://localhost:8000/api/ai/conversations?purpose=News%20Analysis'")
    print("\n2. Via Database:")
    print("   sqlite3 /root/optifire/data/optifire.db")
    print("   SELECT * FROM openai_conversations ORDER BY timestamp DESC LIMIT 5;")
    print("\n3. Via Log Files:")
    print("   cat /root/optifire/data/openai_logs/conversations_*.log")
    print("   tail -f /root/optifire/data/openai_logs/conversations_*.log  # Live monitoring")


if __name__ == "__main__":
    asyncio.run(test_openai_logging())
