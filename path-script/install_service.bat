@echo off
:: Check for administrator privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Yêu cầu quyền Administrator để cài đặt service.
    echo Vui lòng chạy lại file này với quyền Administrator.
    echo Cách chạy với quyền Administrator:
    echo 1. Click chuột phải vào file install_service.bat
    echo 2. Chọn "Run as administrator"
    pause
    exit /b 1
)

:: Check if Python is installed
where python >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Python không được tìm thấy. Vui lòng cài đặt Python trước.
    pause
    exit /b 1
)

:: Check if required files exist
if not exist "PC-bot-service.py" (
    echo File PC-bot-service.py không tồn tại.
    pause
    exit /b 1
)

if not exist "PC-bot.py" (
    echo File PC-bot.py không tồn tại.
    pause
    exit /b 1
)

:: Get full path of current directory
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

echo Installing PC Control Bot Service...
echo Current directory: %CURRENT_DIR%

:: Install service with full path
python "%CURRENT_DIR%\PC-bot-service.py" install
if %errorlevel% NEQ 0 (
    echo Error installing service. Please check the error message above.
    pause
    exit /b 1
)

echo Starting service...
python "%CURRENT_DIR%\PC-bot-service.py" start
if %errorlevel% NEQ 0 (
    echo Error starting service. Please check the error message above.
    pause
    exit /b 1
)

echo Service installed and started successfully!
echo Service name: PCBotService
echo Display name: PC Control Bot Service
echo Location: %CURRENT_DIR%
pause 