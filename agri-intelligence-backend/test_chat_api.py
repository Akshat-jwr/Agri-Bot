"""
🧪 MINIMAL CHAT API TEST
========================

Test only the chat session creation API endpoint to isolate the issue
"""

import asyncio
import sys
import os
import json
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, '/Users/akshatjiwrajka/programming/Capital-One-Agri/agri-intelligence-backend')

from fastapi.testclient import TestClient
from app.main import app

def test_chat_session_creation():
    """Test chat session creation via API"""
    
    print("🧪 Testing chat session creation API...")
    
    client = TestClient(app)
    
    # Step 1: Login to get token
    print("\n1️⃣ Logging in to get token...")
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "demo@farmer.com", "password": "demo123"}
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data["access_token"]
        print(f"✅ Login successful, token: {access_token[:50]}...")
        
        # Step 2: Create chat session
        print("\n2️⃣ Creating chat session...")
        session_response = client.post(
            "/api/v1/chat/sessions",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "title": "API Test Chat Session",
                "language_preference": "hinglish"
            }
        )
        
        print(f"📊 Session response status: {session_response.status_code}")
        print(f"📋 Session response headers: {dict(session_response.headers)}")
        print(f"📄 Session response body: {session_response.text}")
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            print(f"✅ Chat session created successfully!")
            print(f"   Session ID: {session_data.get('id')}")
            print(f"   Title: {session_data.get('title')}")
            print(f"   Language: {session_data.get('language_preference')}")
        else:
            print(f"❌ Failed to create chat session")
            print(f"   Error: {session_response.text}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"   Error: {login_response.text}")

if __name__ == "__main__":
    test_chat_session_creation()
