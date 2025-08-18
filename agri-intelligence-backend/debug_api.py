#!/usr/bin/env python3
"""
Debug script to test the complete Chat API flow
"""
import requests
import asyncio
from typing import Dict, Optional
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import create_access_token
from app.core.config import settings
from sqlalchemy import select

BASE_URL = "http://localhost:8000"

class ChatAPITester:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.session_id: Optional[str] = None
        
    async def get_demo_user_token(self) -> str:
        """Get authentication token for demo user"""
        print("🔑 Getting authentication token...")
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(User.email == "demo@farmer.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise Exception("Demo user not found")
                
            # Create access token
            token = create_access_token(data={"sub": user.email})
            self.user_id = str(user.id)
            self.access_token = token
            
            print(f"✅ Got token for user: {user.email} (ID: {self.user_id})")
            return token
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated API request"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        response.raise_for_status()
        return response.json()
    
    async def test_create_session(self):
        """Test creating a chat session"""
        print("\n📝 Testing session creation...")
        
        session_data = {
            "title": "API Test Session",
            "location_context": {
                "state": "Punjab",
                "district": "Amritsar",
                "tehsil": "Ajnala",
                "village": "Koohli",
                "coordinates": {"lat": 31.63, "lng": 74.87}
            },
            "language_preference": "hinglish"
        }
        
        result = self.make_request("POST", "/api/v1/chat/sessions", session_data)
        self.session_id = result["id"]
        
        print(f"✅ Created session: {result['title']} (ID: {self.session_id})")
        return result
    
    async def test_list_sessions(self):
        """Test listing chat sessions"""
        print("\n📋 Testing session listing...")
        
        result = self.make_request("GET", "/api/v1/chat/sessions")
        
        sessions = result.get("sessions", [])
        total_count = result.get("total_count", 0)
        
        print(f"✅ Found {total_count} sessions")
        for session in sessions[:2]:  # Show first 2
            print(f"   - {session['title']} ({session['id']})")
        
        return result
    
    async def test_send_message(self):
        """Test sending a message"""
        print("\n💬 Testing message sending...")
        
        if not self.session_id:
            raise Exception("No session ID available")
            
        message_data = {
            "session_id": self.session_id,
            "content": "What's the best time to plant rice in Punjab?"
        }
        
        print(f"📤 Sending message: {message_data['content']}")
        result = self.make_request("POST", "/api/v1/chat/messages", message_data)
        
        print(f"✅ Message sent successfully!")
        print(f"   User Message ID: {result[0]['id']}")
        print(f"   AI Response (first 100 chars): {result[1]['content'][:100]}...")
        
        return result
    
    async def run_complete_test(self):
        """Run complete API test flow"""
        try:
            print("🚀 Starting complete Chat API test...\n")
            
            # Get authentication
            await self.get_demo_user_token()
            
            # Test session creation
            await self.test_create_session()
            
            # Test session listing
            await self.test_list_sessions()
            
            # Test message sending
            await self.test_send_message()
            
            print("\n🎉 All API tests passed successfully!")
            
        except Exception as e:
            print(f"\n❌ API test failed: {e}")
            import traceback
            traceback.print_exc()

async def main():
    tester = ChatAPITester()
    await tester.run_complete_test()

if __name__ == "__main__":
    asyncio.run(main())
