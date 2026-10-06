@echo off
setlocal
cd /d "%~dp0"
echo Preparando a Vitrine Virtual...
python --version >nul 2>&1
if errorlevel 1 (
  echo Instale o Python 3.10 ou superior e marque Add Python to PATH.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 goto erro
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto erro
echo.
echo Abra http://127.0.0.1:5000 no navegador.
echo Para encerrar, pressione Ctrl+C.
".venv\Scripts\python.exe" run.py
if errorlevel 1 goto erro
exit /b 0
:erro
echo Nao foi possivel iniciar. Confira a mensagem acima.
pause
exit /b 1
