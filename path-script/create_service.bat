@echo off
:: Check for administrator privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Yêu cầu quyền Administrator để tạo service.
    echo Vui lòng chạy lại file này với quyền Administrator.
    echo Cách chạy với quyền Administrator:
    echo 1. Click chuột phải vào file create_service.bat
    echo 2. Chọn "Run as administrator"
    pause
    exit /b 1
)

:: Set Python path manually (update this to your actual Python path)
set "PYTHON_PATH=C:\Users\Dell\AppData\Local\Programs\Python\Python313\python.exe"

:: Verify Python path
if not exist "%PYTHON_PATH%" (
    echo Python không được tìm thấy tại: %PYTHON_PATH%
    echo Vui lòng cài đặt Python hoặc cập nhật đường dẫn trong file create_service.bat
    pause
    exit /b 1
)

:: Get current directory
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

:: Verify script files exist
if not exist "%CURRENT_DIR%\PC-bot-service.py" (
    echo File PC-bot-service.py không tồn tại tại: %CURRENT_DIR%
    pause
    exit /b 1
)

if not exist "%CURRENT_DIR%\PC-bot.py" (
    echo File PC-bot.py không tồn tại tại: %CURRENT_DIR%
    pause
    exit /b 1
)

echo Creating PC Control Bot Service...
echo Python path: %PYTHON_PATH%
echo Script directory: %CURRENT_DIR%

:: Stop and delete existing service if it exists
sc query PCBotService2 >nul 2>&1
if %errorlevel% EQU 0 (
    echo Service đã tồn tại, đang dừng và xóa...
    sc stop PCBotService2
    sc delete PCBotService2
    timeout /t 2 /nobreak >nul
)

:: Create service with full paths
echo Đang tạo service...
sc create PCBotService2 binPath= "\"%PYTHON_PATH%\" \"%CURRENT_DIR%\PC-bot-service.py\"" DisplayName= "PC Control Bot Service 2" start= auto
if %errorlevel% NEQ 0 (
    echo Error creating service. Please check the error message above.
    pause
    exit /b 1
)

:: Set description
echo Đang cài đặt mô tả service...
sc description PCBotService2 "Telegram bot service for controlling PC"
if %errorlevel% NEQ 0 (
    echo Error setting service description.
    pause
    exit /b 1
)

:: Start service
echo Đang khởi động service...
sc start PCBotService2
if %errorlevel% NEQ 0 (
    echo Error starting service. Please check the error message above.
    pause
    exit /b 1
)

echo Service created and started successfully!
echo Service name: PCBotService2
echo Display name: PC Control Bot Service 2
echo Location: %CURRENT_DIR%
echo.
echo Kiểm tra service trong Services Manager (services.msc)
pause 