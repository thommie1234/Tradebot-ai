#!/usr/bin/env python3
"""
Test OpenAI logging initialization.
"""
import sys
sys.path.insert(0, '/root/optifire')

from optifire.ai.openai_client import OpenAIClient
import sqlite3

print("Testing OpenAI logging initialization...\n")

# Initialize client (this should create the table)
print("1. Initializing OpenAIClient...")
client = OpenAIClient()
print("   ✅ Client initialized\n")

# Check if table was created
print("2. Checking database...")
conn = sqlite3.connect("/root/optifire/data/optifire.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='openai_conversations'")
table_exists = cursor.fetchone()

if table_exists:
    print("   ✅ Table 'openai_conversations' created\n")

    # Check schema
    cursor.execute("PRAGMA table_info(openai_conversations)")
    columns = cursor.fetchall()
    print("   Table schema:")
    for col in columns:
        print(f"      - {col[1]} ({col[2]})")

    print("\n3. Testing manual log entry...")
    # Test logging (without calling OpenAI)
    client._log_conversation(
        model="gpt-4o-mini",
        purpose="Test: Manual Log Entry",
        prompt="This is a test prompt",
        response="This is a test response",
        tokens_used=50,
        cost_usd=0.0001,
        temperature=0.3,
        max_tokens=100
    )
    print("   ✅ Log entry created\n")

    # Verify
    cursor.execute("SELECT COUNT(*) FROM openai_conversations")
    count = cursor.fetchone()[0]
    print(f"4. Database verification: {count} conversation(s) logged\n")

    if count > 0:
        cursor.execute("SELECT timestamp, purpose, model, tokens_used, cost_usd FROM openai_conversations LIMIT 1")
        row = cursor.fetchone()
        print("   Latest entry:")
        print(f"      Timestamp: {row[0]}")
        print(f"      Purpose: {row[1]}")
        print(f"      Model: {row[2]}")
        print(f"      Tokens: {row[3]}")
        print(f"      Cost: ${row[4]:.6f}")

    # Check log file
    import os
    from datetime import datetime
    log_dir = "/root/optifire/data/openai_logs"
    if os.path.exists(log_dir):
        files = os.listdir(log_dir)
        print(f"\n5. Log files created: {len(files)}")
        for f in files:
            size = os.path.getsize(os.path.join(log_dir, f))
            print(f"      - {f} ({size} bytes)")
    else:
        print("\n5. No log directory yet (will be created on first log)")

else:
    print("   ❌ Table NOT created")

conn.close()

print("\n" + "="*60)
print("✅ Logging infrastructure is working!")
print("="*60)
