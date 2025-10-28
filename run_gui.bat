@echo off
chcp 65001 >nul
echo ========================================
echo 多语言语音识别系统 - GUI 版本
echo ========================================
echo.

python gui_app.py

if errorlevel 1 (
    echo.
    echo 启动失败！
    pause
)
