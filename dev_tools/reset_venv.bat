@echo off
REM Réinitialisation de l'environnement virtuel CrazyTerm
cd /d "%~dp0.."
if exist .venv rmdir /s /q .venv
python -m venv .venv
