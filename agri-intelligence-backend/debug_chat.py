"""
🔍 CHAT SYSTEM DEBUG SCRIPT
===========================

Test the chat system components step by step to find the issue
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, '/Users/akshatjiwrajka/programming/Capital-One-Agri/agri-intelligence-backend')

from app.core.database import get_db
from app.services.chat_service import chat_service
from app.schemas.chat import ChatSessionCreate
from app.models.user import User
from sqlalchemy import select

async def debug_chat_system():
    """Debug the chat system step by step"""
    
    print("🔍 Starting chat system debug...")
    
    try:
        # Test 1: Database connection
        print("\n1️⃣ Testing database connection...")
        async for db in get_db():
            print("✅ Database connection successful")
            
            # Test 2: Find demo user
            print("\n2️⃣ Finding demo user...")
            result = await db.execute(
                select(User).filter(User.email == "demo@farmer.com")
            )
            user = result.scalar_one_or_none()
            
            if user:
                print(f"✅ Found user: {user.email} (ID: {user.id})")
                print(f"   User type: {type(user.id)}")
                print(f"   Is active: {user.is_active}")
                print(f"   Is verified: {user.is_verified}")
                
                # Test 3: Create session data
                print("\n3️⃣ Creating session data...")
                session_data = ChatSessionCreate(
                    title="Test Wheat Growing Help",
                    language_preference="hinglish"
                )
                print(f"✅ Session data created: {session_data}")
                
                # Test 4: Create chat session
                print("\n4️⃣ Creating chat session...")
                try:
                    session = await chat_service.create_session(
                        db=db,
                        user_id=str(user.id),  # Convert to string
                        session_data=session_data
                    )
                    print(f"✅ Chat session created successfully!")
                    print(f"   Session ID: {session.id}")
                    print(f"   Title: {session.title}")
                    print(f"   User ID: {session.user_id}")
                    print(f"   Language: {session.language_preference}")
                    
                except Exception as e:
                    print(f"❌ Failed to create chat session: {e}")
                    import traceback
                    traceback.print_exc()
                
            else:
                print("❌ Demo user not found")
            
            break  # Only use first db connection
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_chat_system())
