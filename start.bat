@echo off
echo ========================================
echo LANCEMENT INTERFACE STREAMLIT
echo ========================================
echo.

echo Activation environnement virtuel...
call venv\Scripts\activate.bat
echo.

echo Demarrage Streamlit...
streamlit run app.py

pause
