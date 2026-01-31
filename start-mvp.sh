#!/bin/bash
# Script de démarrage pour MVP Insurance - Pitch Investisseurs

echo ""
echo "================================================"
echo "   INSURANCE MVP - STARTUP MULTI-SERVICES"
echo "================================================"
echo ""

echo "[1/3] Installation des dépendances Python (Backend)..."
cd backend
pip install -r requirements.txt > /dev/null 2>&1

echo "[2/3] Installation des dépendances Node (Frontend Client)..."
cd ../frontend-client
npm install > /dev/null 2>&1

echo "[3/3] Installation des dépendances Node (Frontend Advisor)..."
cd ../frontend-advisor
npm install > /dev/null 2>&1

echo ""
echo "================================================"
echo "   DÉMARRAGE DES SERVICES"
echo "================================================"
echo ""

# Lancer le backend
echo "Démarrage Backend FastAPI (port 8000)..."
cd ../backend
python main.py &
BACKEND_PID=$!

# Attendre que le backend soit prêt
sleep 3

# Lancer les frontends
echo "Démarrage Frontend Client (port 3000)..."
cd ../frontend-client
npm run dev &
CLIENT_PID=$!

echo "Démarrage Frontend Advisor (port 3001)..."
cd ../frontend-advisor
npm run dev &
ADVISOR_PID=$!

echo ""
echo "================================================"
echo "   SERVICES LANCÉS"
echo "================================================"
echo ""
echo "✅ Backend FastAPI:    http://localhost:8000"
echo "✅ Frontend Client:    http://localhost:3000"
echo "✅ Frontend Advisor:   http://localhost:3001"
echo ""
echo "📋 API Docs:          http://localhost:8000/docs"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter tous les services"

# Attendre
wait
