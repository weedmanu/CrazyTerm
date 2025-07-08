@echo off
echo 🚀 Validation de la qualité du code CrazyTerm...
echo.
cd /d "%~dp0"
python "dev_tools\quality_validator.py"
pause
