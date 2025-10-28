@echo off
chcp 65001 >nul
echo ========================================
echo VAD + ASR 語音識別系統
echo ========================================
echo.
echo 選擇執行模式:
echo [1] 完整應用 (推薦)
echo [2] 基礎範例
echo [3] VTuber 範例
echo [4] 執行測試
echo [5] 下載模型
echo.
set /p choice="請輸入數字 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 啟動完整應用...
    python app.py
) else if "%choice%"=="2" (
    echo.
    echo 啟動基礎範例...
    python examples/basic_usage.py
) else if "%choice%"=="3" (
    echo.
    echo 啟動 VTuber 範例...
    python examples/vtuber_demo.py
) else if "%choice%"=="4" (
    echo.
    echo 執行測試...
    python simple_test.py
) else if "%choice%"=="5" (
    echo.
    echo 下載模型...
    python download_models.py
) else (
    echo.
    echo 無效選擇！
)

echo.
pause
