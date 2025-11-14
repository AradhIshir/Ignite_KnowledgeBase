#!/bin/bash

# Ignite Knowledge - Application Startup Script
# This script helps you run both backend and frontend services

echo "🚀 Ignite Knowledge Application Startup"
echo "========================================"
echo ""
echo "Choose an option:"
echo "1. Run Backend only (FastAPI on port 8080)"
echo "2. Run Frontend only (Next.js on port 3000)"
echo "3. Run Both (requires 2 terminal windows)"
echo ""
read -p "Enter your choice (1/2/3): " choice

case $choice in
  1)
    echo "Starting Backend..."
    cd backend
    poetry run uvicorn app.main:app --reload --port 8080
    ;;
  2)
    echo "Starting Frontend..."
    cd frontend
    npm run dev
    ;;
  3)
    echo "To run both services, open 2 terminal windows:"
    echo ""
    echo "Terminal 1 (Backend):"
    echo "  cd backend"
    echo "  poetry run uvicorn app.main:app --reload --port 8080"
    echo ""
    echo "Terminal 2 (Frontend):"
    echo "  cd frontend"
    echo "  npm run dev"
    echo ""
    echo "Then access the app at: http://localhost:3000"
    ;;
  *)
    echo "Invalid choice"
    ;;
esac

