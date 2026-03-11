@echo off
echo ===============================
echo Cleaning old build files...
echo ===============================

rmdir /s /q build
rmdir /s /q dist
del clock.spec

echo Clean complete!
echo ===============================
pause