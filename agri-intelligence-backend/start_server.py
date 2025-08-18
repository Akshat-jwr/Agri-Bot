#!/usr/bin/env python3
"""
🚀 AGRICULTURAL INTELLIGENCE SERVER LAUNCHER
===========================================

Starts the complete agricultural intelligence FastAPI server with:
- Chat system with sessions and messages
- Authentication system
- Perfect multilingual support
- Fact-checking capabilities
- RAG system with 11 agricultural experts

Ready to serve farmers across India! 🌾
"""

import os
import sys
import uvicorn

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("🌾 Starting Agricultural Intelligence Server...")
    print(f"📁 Working directory: {current_dir}")
    print(f"🐍 Python path: {sys.path[0]}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[current_dir]
    )
