@echo off
REM ================================================
REM   INSURANCE MVP - SCRIPT DE DEMARRAGE
REM   (Architecture FastAPI + React pour investisseurs)
REM ================================================

color 0A
title Insurance MVP - Launcher

echo.
echo ================================================
echo.
echo   ██████╗ ███████╗████████╗██╗  ██╗███╗   ███╗
echo   ██╔══██╗██╔════╝╚══██╔══╝██║  ██║████╗ ████║
echo   ██████╔╝█████╗     ██║   ███████║██╔████╔██║
echo   ██╔══██╗██╔══╝     ██║   ██╔══██║██║╚██╔╝██║
echo   ██████╔╝███████╗   ██║   ██║  ██║██║ ╚═╝ ██║
echo   ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝
echo.
echo   GESTION COGNITIVE DES SINISTRES
echo   MVP pour Pitch Investisseurs
echo.
echo ================================================
echo.

REM Vérifier si les répertoires existent
if not exist backend (
    echo ❌ Erreur: Dossier 'backend' non trouvé
    pause
    exit /b 1
)

if not exist frontend-client (
    echo ❌ Erreur: Dossier 'frontend-client' non trouvé
    pause
    exit /b 1
)

if not exist frontend-advisor (
    echo ❌ Erreur: Dossier 'frontend-advisor' non trouvé
    pause
    exit /b 1
)

echo [✓] Structure validée
echo.

REM Menu
echo Choisissez une option:
echo.
echo 1 - Lancer TOUS les services (backend + 2 frontends)
echo 2 - Lancer BACKEND SEUL (http://localhost:8000)
echo 3 - Lancer FRONTEND CLIENT (http://localhost:3000)
echo 4 - Lancer FRONTEND ADVISOR (http://localhost:3001)
echo 5 - Afficher API Docs (http://localhost:8000/docs)
echo 6 - Installer les dépendances
echo 0 - Quitter
echo.

set /p choice="Entrez votre choix (0-6): "

if "%choice%"=="1" goto all
if "%choice%"=="2" goto backend
if "%choice%"=="3" goto client
if "%choice%"=="4" goto advisor
if "%choice%"=="5" goto docs
if "%choice%"=="6" goto install
if "%choice%"=="0" exit /b 0

echo ❌ Choix invalide
pause
goto start

:all
echo.
echo ================================================
echo   DÉMARRAGE DE TOUS LES SERVICES
echo ================================================
echo.

echo [1/3] Lancement Backend FastAPI (port 8000)...
cd backend
start "Backend FastAPI" cmd /k "python main.py"
timeout /t 3 /nobreak

cd ..
echo [2/3] Lancement Frontend Client (port 3000)...
cd frontend-client
start "Frontend Client" cmd /k "npm run dev"

echo [3/3] Lancement Frontend Advisor (port 3001)...
cd ..\frontend-advisor
start "Frontend Advisor" cmd /k "npm run dev"

cd ..
echo.
echo ================================================
echo   TOUS LES SERVICES SONT EN COURS DE DÉMARRAGE
echo ================================================
echo.
echo ✅ Backend FastAPI:    http://localhost:8000
echo ✅ Frontend Client:    http://localhost:3000
echo ✅ Frontend Advisor:   http://localhost:3001
echo ✅ API Docs:          http://localhost:8000/docs
echo.
echo Fermerez chaque fenêtre pour arrêter les services
echo.
pause
goto end

:backend
echo.
echo Lancement du Backend FastAPI...
echo.
cd backend
python main.py
goto end

:client
echo.
echo Lancement du Frontend Client...
echo.
cd frontend-client
npm run dev
goto end

:advisor
echo.
echo Lancement du Frontend Advisor...
echo.
cd frontend-advisor
npm run dev
goto end

:docs
echo.
echo Ouverture des API Docs...
start http://localhost:8000/docs
timeout /t 2 /nobreak
goto start

:install
echo.
echo Installation des dépendances...
echo.

echo [1/3] Backend Python...
cd backend
call pip install -r requirements.txt

echo [2/3] Frontend Client Node...
cd ..\frontend-client
call npm install

echo [3/3] Frontend Advisor Node...
cd ..\frontend-advisor
call npm install

echo.
echo ✅ Toutes les dépendances sont installées
echo.
pause
goto start

:end
exit /b 0
