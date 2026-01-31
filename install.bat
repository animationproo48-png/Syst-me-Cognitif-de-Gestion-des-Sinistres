@echo off
echo ========================================
echo INSTALLATION SYSTEME COGNITIF SINISTRES
echo ========================================
echo.

echo [1/3] Creation environnement virtuel...
python -m venv venv
echo.

echo [2/3] Activation environnement...
call venv\Scripts\activate.bat
echo.

echo [3/3] Installation dependances...
pip install -r requirements.txt
echo.

echo ========================================
echo INSTALLATION TERMINEE!
echo ========================================
echo.
echo Pour lancer le systeme:
echo   1. Tests: python test_system.py
echo   2. Demo CLI: python demo.py
echo   3. Interface Web: streamlit run app.py
echo.
pause
