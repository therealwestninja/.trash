@echo off
cd /d "%~dp0"
echo Starting CERBERUS Companion server...
echo Open http://localhost:8000/PythonServer.html in Chrome
start "" "http://localhost:8000/PythonServer.html"
python -m http.server 8000
pause
