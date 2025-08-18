"""
🔍 MESSAGE SENDING DEBUG SCRIPT
===============================

Test the message sending functionality step by step
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, '/Users/akshatjiwrajka/programming/Capital-One-Agri/agri-intelligence-backend')

from app.core.database import get_db
from app.services.chat_service import chat_service
from app.schemas.chat import ChatMessageCreate
from app.models.user import User
from sqlalchemy import select

async def debug_message_sending():
    """Debug the message sending step by step"""
    
    print("🔍 Starting message sending debug...")
    
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
                
                # Test 3: Get existing session
                print("\n3️⃣ Getting existing session...")
                session_id = "92696e78-ab08-4c64-9184-4be6131b2fde"
                session = await chat_service.get_session(db, session_id, str(user.id))
                
                if session:
                    print(f"✅ Found session: {session.title}")
                    
                    # Test 4: Create message data
                    print("\n4️⃣ Creating message data...")
                    message_data = ChatMessageCreate(
                        session_id=session_id,
                        content="Hey, how do I grow wheat?",
                        language_preference="english"
                    )
                    print(f"✅ Message data created: {message_data}")
                    
                    # Test 5: Send simple message
                    print("\n5️⃣ Sending message...")
                    try:
                        user_message, ai_message = await chat_service.send_message(
                            db=db,
                            user_id=str(user.id),
                            message_data=message_data
                        )
                        print(f"✅ Message sent successfully!")
                        print(f"   User Message ID: {user_message.id}")
                        print(f"   AI Message ID: {ai_message.id}")
                        print(f"   AI Response: {ai_message.content[:100]}...")
                        
                    except Exception as e:
                        print(f"❌ Failed to send message: {e}")
                        import traceback
                        traceback.print_exc()
                
                else:
                    print("❌ Session not found")
            else:
                print("❌ Demo user not found")
            
            break  # Only use first db connection
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_message_sending())
