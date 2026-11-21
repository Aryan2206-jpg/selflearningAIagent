@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
 echo Python is not installed. Install Python 3.10+ from python.org and try again.
 pause
 exit /b
)
if not exist .venv (
 python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install -q -r requirements.txt
python -m streamlit run app.py
pause
