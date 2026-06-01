@echo off
chcp 65001 >nul
title RAG 智库系统启动器

echo ========================================
echo   RAG 智库系统 - 启动脚本
echo ========================================
echo.

echo [1/5] 启动 Docker 服务...
cd /d "%~dp0docker"
docker-compose.exe start
docker-compose.exe up -d
echo      Docker 服务已启动

echo.
echo [2/5] 等待 Docker 容器就绪...
docker wait milvus-standalone >nul 2>&1
echo      容器已就绪

cd /d "%~dp0"
echo [3/5] 启动后端服务 (FastAPI)...
start "FastAPI" "%~dp0.venv\Scripts\python.exe" -m src.main

echo      等待后端启动...
:wait_backend
timeout /t 2 /nobreak >nul
curl -s -o /dev/null -w "%%{http_code}" http://localhost:8000/docs >nul 2>&1
if errorlevel 1 goto wait_backend
echo      后端已就绪

timeout /t 1 /nobreak >nul

echo      启动 Celery Worker...
start "Celery" "%~dp0.venv\Scripts\python.exe" -m celery -A src.worker.celery_app worker --loglevel=info -P solo

echo.
echo [4/5] 启动前端服务 (Vue)...
cd /d "%~dp0frontend"
start "Vue" cmd /c "npm run dev"

echo      等待前端就绪...
:wait_frontend
timeout /t 2 /nobreak >nul
curl -s -o /dev/null -w "%%{http_code}" http://localhost:5173 >nul 2>&1
if errorlevel 1 goto wait_frontend
echo      前端已就绪

echo.
echo [5/5] 打开浏览器...
start http://localhost:5173

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo   访问地址:
echo   - 前端页面:   http://localhost:5173
echo   - API 文档:   http://localhost:8000/docs
echo   - Flower:     http://localhost:5555
echo   - MinIO:      http://localhost:9001
echo   - RabbitMQ:   http://localhost:15672
echo.
echo 按任意键退出此窗口（服务继续运行）...
pause >nul