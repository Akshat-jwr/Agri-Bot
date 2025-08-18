#!/bin/bash

# 🚀 Perfect Agricultural AI Platform Startup Script
# This script starts both backend and frontend services

echo "🌾 Starting Perfect Agricultural AI Platform..."

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
}

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
if check_port 8000; then
    echo "   Stopping backend on port 8000..."
    kill -9 $(lsof -t -i:8000) 2>/dev/null || true
fi

if check_port 3001; then
    echo "   Stopping frontend on port 3001..."
    kill -9 $(lsof -t -i:3001) 2>/dev/null || true
fi

sleep 2

# Start backend
echo "🔧 Starting Enhanced Backend with Fact Checker..."
cd /Users/akshatjiwrajka/programming/Capital-One-Agri/agri-intelligence-backend
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend connectivity
echo "🩺 Testing backend health..."
if curl -s http://localhost:8000/api/v1/health/status > /dev/null; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend health check failed"
fi

# Start frontend
echo "🎨 Starting Enhanced Frontend..."
cd /Users/akshatjiwrajka/programming/Capital-One-Agri/agri-frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Perfect Agricultural AI Platform Started!"
echo "📱 Frontend: http://localhost:3001"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "✨ Your enterprise-level agricultural platform is ready!"

# Keep script running
wait
