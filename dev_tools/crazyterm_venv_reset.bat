@echo off
chcp 65001 >nul
REM Script batch pour reinitialiser l'environnement virtuel CrazyTerm hors venv
cd /d %~dp0..

REM Vérifie si le venv est actif (variable d'environnement)
if not "%VIRTUAL_ENV%"=="" (
    echo [INFO] Un venv Python est actif. Fermeture de ce terminal recommandee.
    exit /b 1
)

REM ==================== [ETAPE 1] Nettoyage des anciens environnements ====================
echo.
echo ==================== [ETAPE 1] Nettoyage des anciens environnements ====================
set CLEANED=0
for %%D in (.venv venv env myvenv) do (
    if exist %%D (
        echo [INFO] Suppression de l'environnement virtuel existant %%D
        rmdir /s /q %%D 2>nul
        set CLEANED=1
    )
)
if %CLEANED%==1 (
    echo [OK] Nettoyage termine.
) else (
    echo [OK] Aucun environnement virtuel a supprimer.
)

REM ==================== [ETAPE 2] Creation du nouvel environnement ====================
echo.
echo ==================== [ETAPE 2] Creation du nouvel environnement ====================
echo Nom du venv : .venv
set VENV_DIR=.venv
echo Chemin complet : %CD%\%VENV_DIR%
echo Python utilise :
where python
python --version
python -m venv %VENV_DIR%
if not exist %VENV_DIR%\Scripts\activate.bat (
    echo [ERREUR] La creation du venv a echoue.
    exit /b 2
)
echo [OK] Environnement virtuel cree a %CD%\%VENV_DIR%.

REM ==================== [ETAPE 3] Installation des dependances ====================
echo.
echo ==================== [ETAPE 3] Installation des dependances ====================
REM Activation du venv
call %VENV_DIR%\Scripts\activate.bat
echo.
echo [INFO] --> Installation des dependances du projet : requirements.txt
if exist requirements.txt (
    echo Contenu de requirements.txt :
    type requirements.txt
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo [OK] requirements.txt installe.
) else (
    echo [WARN] Aucun requirements.txt trouve.
)
echo.
echo [INFO] --> Installation des dependances de developpement : dev_requirements.txt
if exist dev_requirements.txt (
    echo Contenu de dev_requirements.txt :
    type dev_requirements.txt
    pip install -r dev_requirements.txt
    echo [OK] dev_requirements.txt installe.
) else (
    echo [INFO] Installation de flake8 et pylint (dependances de base dev)
    pip install flake8 pylint
    echo [OK] flake8 et pylint installes.
)

REM ==================== [ETAPE 4] Finalisation ====================
echo.
echo ==================== [ETAPE 4] Finalisation ====================
REM Desactivation du venv
call %VENV_DIR%\Scripts\deactivate.bat
if exist %VENV_DIR% (
    echo.
    echo [OK] L'environnement virtuel CrazyTerm est pret et fonctionnel !
    echo Vous pouvez maintenant utiliser le projet en toute securite.
    exit /b 0
) else (
    echo.
    echo [ERREUR] La reinitialisation du venv a echoue. Consultez les messages ci-dessus.
    exit /b 3
)
