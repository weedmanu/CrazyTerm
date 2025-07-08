@echo off
:: =============================================================================
:: Script d'installation et build automatique CrazySerialTerm
:: Version autonome - ne nécessite aucune installation préalable
:: =============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0\.."

echo.
echo ========================================================
echo     INSTALLATION AUTONOME CRAZYSERIALTERM
echo ========================================================
echo.
echo Ce script va :
echo - Detecter/installer Python si necessaire
echo - Creer un environnement virtuel
echo - Installer toutes les dependances
echo - Generer l'executable
echo.
pause

:: Vérifier si Python est installé
echo [ETAPE 1/6] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ATTENTION] Python non detecte sur le systeme
    echo.
    echo INSTALLATION REQUISE :
    echo 1. Allez sur https://python.org/downloads/
    echo 2. Telechargez Python 3.11 ou superieur
    echo 3. IMPORTANT : Cochez "Add Python to PATH" lors de l'installation
    echo 4. Relancez ce script apres installation
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Python detecte
    python --version
)

:: Vérifier la version de Python
echo [ETAPE 2/6] Verification de la version Python...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python 3.8 ou superieur requis
    python -c "import sys; print(f'Version detectee: {sys.version}')"
    pause
    exit /b 1
) else (
    echo [OK] Version Python compatible
)

:: Créer l'environnement virtuel
echo [ETAPE 3/6] Creation de l'environnement virtuel...
if not exist ".venv" (
    echo Creation du dossier .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERREUR] Echec creation environnement virtuel
        pause
        exit /b 1
    )
    echo [OK] Environnement virtuel cree
) else (
    echo [OK] Environnement virtuel existe deja
)

:: Activer l'environnement virtuel et installer les dépendances
echo [ETAPE 4/6] Installation des dependances...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)

echo Installation de pip (mise a jour)...
python -m pip install --upgrade pip --quiet

echo Installation des dependances principales...
pip install PyQt5>=5.15.0 pyserial>=3.5 pyinstaller>=6.0 --quiet
if errorlevel 1 (
    echo [ERREUR] Echec installation des dependances
    pause
    exit /b 1
)

echo [OK] Toutes les dependances installees

:: Nettoyer les anciens builds
echo [ETAPE 5/6] Preparation du build...
if exist "dist" rmdir /s /q "dist"
if exist "build\temp" rmdir /s /q "build\temp"
if exist "build\*.spec" del /q "build\*.spec"

mkdir "dist" 2>nul
mkdir "build\temp" 2>nul

echo [OK] Dossiers de build prepares

:: Générer l'exécutable
echo [ETAPE 6/6] Generation de l'executable...
echo Ceci peut prendre quelques minutes...
echo.

:: Obtenir le chemin absolu de l'icône
set "PROJECT_PATH=%CD%"
set "ICON_PATH="
if exist "assets\CrazySerialTerm.ico" (
    set "ICON_PATH=%PROJECT_PATH%\assets\CrazySerialTerm.ico"
    echo [INFO] Icone trouvee : !ICON_PATH!
)

:: Générer avec ou sans icône
if defined ICON_PATH (
    python -m PyInstaller ^
        --onefile ^
        --windowed ^
        --name "CrazySerialTerm" ^
        --icon "!ICON_PATH!" ^
        --distpath "dist" ^
        --workpath "build\temp" ^
        --specpath "build" ^
        --noconsole ^
        --hidden-import "PyQt5.QtCore" ^
        --hidden-import "PyQt5.QtGui" ^
        --hidden-import "PyQt5.QtWidgets" ^
        --hidden-import "serial" ^
        crazyserialterm.py
) else (
    python -m PyInstaller ^
        --onefile ^
        --windowed ^
        --name "CrazySerialTerm" ^
        --distpath "dist" ^
        --workpath "build\temp" ^
        --specpath "build" ^
        --noconsole ^
        --hidden-import "PyQt5.QtCore" ^
        --hidden-import "PyQt5.QtGui" ^
        --hidden-import "PyQt5.QtWidgets" ^
        --hidden-import "serial" ^
        crazyserialterm.py
)

if errorlevel 1 (
    echo [ERREUR] Echec generation executable
    pause
    exit /b 1
)

:: Vérifier que l'exécutable a été créé
if not exist "dist\CrazySerialTerm.exe" (
    echo [ERREUR] Executable non trouve dans dist\
    pause
    exit /b 1
)

:: Créer un package portable
echo Creation du package portable...
if not exist "dist\portable" mkdir "dist\portable"
copy "dist\CrazySerialTerm.exe" "dist\portable\" >nul
if exist "assets\CrazySerialTerm.ico" copy "assets\CrazySerialTerm.ico" "dist\portable\" >nul

:: Créer un README pour l'utilisateur final
(
echo # CrazySerialTerm - Application Portable
echo.
echo ## Utilisation
echo 1. Double-cliquez sur CrazySerialTerm.exe
echo 2. L'application se lance directement
echo.
echo ## Informations
echo - Version : Portable
echo - Aucune installation requise
echo - Fonctionne sur Windows 10/11
echo.
echo ## Support
echo - GitHub : https://github.com/[votre-repo]/CrazySerialTerm
echo.
echo Date de generation : %date% %time%
) > "dist\portable\README.txt"

echo.
echo ========================================================
echo          INSTALLATION TERMINEE AVEC SUCCES!
echo ========================================================
echo.
echo FICHIERS GENERES:
echo - Executable principal : dist\CrazySerialTerm.exe
echo - Package portable     : dist\portable\
echo.
echo INFORMATIONS:
for %%i in ("dist\CrazySerialTerm.exe") do (
    echo - Taille executable : %%~zi octets ^(~%%= %%~zi / 1024 / 1024 %% MB^)
    echo - Date creation     : %%~ti
)
echo.
echo UTILISATION:
echo 1. Test immediat    : dist\CrazySerialTerm.exe
echo 2. Package portable : dist\portable\
echo 3. Distribution     : Partagez le dossier dist\portable\
echo.
echo PROCHAINES ETAPES:
echo - Testez l'executable
echo - Le dossier dist\portable\ peut etre distribue independamment
echo - Aucune installation Python requise sur les autres PC
echo.
pause
