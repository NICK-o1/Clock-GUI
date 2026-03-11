@echo off
echo ===============================
echo Building clock.exe...
echo ===============================

python -m PyInstaller --noconsole --onefile --add-data "config.cfg;." clock.py

echo.
echo Build complete!
echo Your EXE is in the /dist folder.
echo ===============================
pause