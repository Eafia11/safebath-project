@echo off
setlocal
cd /d "%~dp0\.."
uvicorn backend.app.main:app --reload
