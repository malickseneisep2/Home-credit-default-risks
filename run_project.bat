@echo off
echo ===================================================
echo   Diagnostic et Lancement - Home Credit API
echo ===================================================

echo [1/2] Tentative de lancement de l'API...
echo (Si cette fenetre se referme, lancez 'uvicorn app.main:app' manuellement)
start cmd /k "echo Lancement de l'API... && uvicorn app.main:app --reload || pause"

echo [2/2] Lancement du Dashboard Streamlit...
streamlit run app.py

pause
