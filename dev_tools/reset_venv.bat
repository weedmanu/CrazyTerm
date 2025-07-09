@echo off
REM Script batch pour réinitialiser l'environnement virtuel CrazyTerm hors venv
cd /d %~dp0..
REM Vérifie si le venv est actif (variable d'environnement)
if not "%VIRTUAL_ENV%"=="" (
    echo [INFO] Un venv Python est actif. Fermeture de ce terminal recommandée.
    exit /b 1
)
REM Suppression de tous les environnements virtuels présents (.venv, venv, env, myvenv, etc.)
echo.
echo [36m==================== [ETAPE 1] Nettoyage des anciens environnements ====================[0m
set CLEANED=0
for %%D in (.venv venv env myvenv) do (
    if exist %%D (
        echo [33m[INFO][0m Suppression de l'environnement virtuel existant %%D
        rmdir /s /q %%D 2>nul
        set CLEANED=1
    )
)
if %CLEANED%==1 (
    echo [32m[OK][0m Nettoyage terminé.
) else (
    echo [32m[OK][0m Aucun environnement virtuel à supprimer.
)
echo.
echo [36m==================== [ETAPE 2] Création du nouvel environnement ====================[0m
echo Nom du venv : .venv
set VENV_DIR=.venv
echo Chemin complet : %CD%\%VENV_DIR%
echo Python utilisé :
where python
python --version
python -m venv %VENV_DIR%
if not exist %VENV_DIR%\Scripts\activate.bat (
    echo [31m[ERREUR][0m La création du venv a échoué.
    exit /b 2
)
echo [32m[OK][0m Environnement virtuel créé à %CD%\%VENV_DIR%.
echo.
echo [36m==================== [ETAPE 3] Installation des dépendances ====================[0m
REM Activation du venv
call %VENV_DIR%\Scripts\activate.bat
echo.
echo [36m[INFO][0m --> Installation des dépendances du projet : requirements.txt
if exist requirements.txt (
    echo Contenu de requirements.txt :
    type requirements.txt
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo [32m[OK][0m requirements.txt installé.
) else (
    echo [33m[WARN][0m Aucun requirements.txt trouvé.
)
echo.
echo [36m[INFO][0m --> Installation des dépendances de développement : dev_requirements.txt
if exist dev_requirements.txt (
    echo Contenu de dev_requirements.txt :
    type dev_requirements.txt
    pip install -r dev_requirements.txt
    echo [32m[OK][0m dev_requirements.txt installé.
) else (
    echo [33m[INFO][0m Installation de flake8 et pylint (dépendances de base dev)
    pip install flake8 pylint
    echo [32m[OK][0m flake8 et pylint installés.
)
echo.
echo [36m==================== [ETAPE 4] Finalisation ====================[0m
REM Désactivation du venv
call %VENV_DIR%\Scripts\deactivate.bat
if exist %VENV_DIR% (
    echo.
    echo [32m[OK][0m L'environnement virtuel CrazyTerm est prêt et fonctionnel !
    echo Vous pouvez maintenant utiliser le projet en toute sécurité.
    exit /b 0
) else (
    echo.
    echo [31m[ERREUR][0m La réinitialisation du venv a échoué. Consultez les messages ci-dessus.
    exit /b 3
)
