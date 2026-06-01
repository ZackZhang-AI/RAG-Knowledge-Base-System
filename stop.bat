@echo off
chcp 65001 >nul
echo ========================================
echo   RAG 智库系统 - 停止脚本
echo ========================================
echo.

echo [1/2] 停止 Docker 服务...
cd /d "%~dp0docker"
"C:\Program Files\Docker\Docker resources\bin\docker-compose.exe" down

echo.
echo [2/2] 停止本地服务...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq FastAPI*" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Celery*" 2>nul
taskkill /F /IM node.exe 2>nul

echo.
echo ========================================
echo   所有服务已停止
echo ========================================
pause