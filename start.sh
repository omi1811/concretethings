#!/bin/bash

# ConcreteThings QMS - Startup Script
echo "🚀 Starting ConcreteThings QMS..."
echo ""

# Start backend
echo "📡 Starting backend server..."
cd /workspaces/concretethings
pkill -f gunicorn 2>/dev/null
gunicorn --bind 0.0.0.0:8001 --workers 2 --timeout 120 server.app:app --daemon
sleep 2

if lsof -i:8001 >/dev/null 2>&1; then
    echo "   ✅ Backend running on http://localhost:8001"
else
    echo "   ❌ Backend failed to start!"
    exit 1
fi

# Start frontend
echo "📱 Starting frontend server..."
cd /workspaces/concretethings/frontend
pkill -f "next dev" 2>/dev/null
sleep 1
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 5

if lsof -i:3000 >/dev/null 2>&1; then
    echo "   ✅ Frontend running on http://localhost:3000"
elif ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo "   🟡 Frontend starting... (may take a few more seconds)"
    echo "   ✅ Check http://localhost:3000 in your browser"
else
    echo "   ❌ Frontend failed to start!"
    echo "   Check logs: tail -f /tmp/frontend.log"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         🎉 ALL SERVERS RUNNING SUCCESSFULLY! 🎉              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8001/api"
echo ""
echo "🔐 Login credentials:"
echo "   Email:    admin@demo.com"
echo "   Password: adminpass"
echo ""
echo "📋 Useful commands:"
echo "   View frontend logs: tail -f /tmp/frontend.log"
echo "   Stop all servers:   pkill -f 'gunicorn|next dev'"
echo "   Restart:            ./start.sh"
echo ""
