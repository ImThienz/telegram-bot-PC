@echo off
:: Check for administrator privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Yêu cầu quyền Administrator để dừng và gỡ cài đặt service.
    echo Vui lòng chạy lại file này với quyền Administrator.
    echo Cách chạy với quyền Administrator:
    echo 1. Click chuột phải vào file uninstall_service.bat
    echo 2. Chọn "Run as administrator"
    pause
    exit /b 1
)

echo Dừng service PCBotService...
python PC-bot-service.py stop
if %errorlevel% NEQ 0 (
    echo Error stopping service. Please check the error message above.
    pause
    exit /b 1
)

echo Gỡ cài đặt service...
python PC-bot-service.py remove
if %errorlevel% NEQ 0 (
    echo Error removing service. Please check the error message above.
    pause
    exit /b 1
)

echo Service đã được dừng và gỡ cài đặt thành công!
pause 