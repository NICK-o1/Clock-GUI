@echo off
echo ===============================
echo Creating portable ZIP package...
echo ===============================

if not exist dist\clock.exe (
    echo ERROR: clock.exe not found. Build first!
    pause
    exit /b
)

cd dist
powershell Compress-Archive -Path clock.exe, ..\config.cfg -DestinationPath clock-portable.zip -Force
cd ..

echo Portable ZIP created: dist\clock-portable.zip
echo ===============================
pause