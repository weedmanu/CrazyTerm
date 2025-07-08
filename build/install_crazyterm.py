#!/usr/bin/env python3
"""
Script d'installation autonome CrazyTerm (remplace install_crazyterm.bat)

- Vérifie la présence de Python 3.8+
- Crée un environnement virtuel .venv
- Installe les dépendances (PyQt5, pyserial, pyinstaller)
- Génère l'exécutable portable CrazyTerm.exe

Usage :
    python build/install_crazyterm.py
"""
import os
import sys
import subprocess
import shutil

REQUIRED_PYTHON = (3, 8)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BUILD_DIR = os.path.join(PROJECT_ROOT, 'build')
VENV_DIR = os.path.join(PROJECT_ROOT, '.venv')
REQUIREMENTS = ["PyQt5>=5.15.0,<5.16.0", "pyserial>=3.5,<4.0", "pyinstaller>=6.0,<7.0"]
ICON_PATH = os.path.join(PROJECT_ROOT, 'assets', 'CrazyTerm.ico')
MAIN_SCRIPT = os.path.join(PROJECT_ROOT, 'crazyterm.py')
DIST_DIR = os.path.join(PROJECT_ROOT, 'dist')
PORTABLE_DIR = os.path.join(DIST_DIR, 'portable')


def check_python_version():
    if sys.version_info < REQUIRED_PYTHON:
        print(f"[ERREUR] Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} ou supérieur requis.")
        sys.exit(1)
    print(f"[OK] Python {sys.version.split()[0]} détecté.")

def create_venv():
    if not os.path.exists(VENV_DIR):
        print("[ETAPE] Création de l'environnement virtuel...")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
        print("[OK] Environnement virtuel créé.")
    else:
        print("[OK] Environnement virtuel déjà présent.")

def run_in_venv(args: list[str]) -> int:
    """Exécute une commande dans l'environnement virtuel."""
    if os.name == "nt":
        python_bin = os.path.join(VENV_DIR, "Scripts", "python.exe")
        pip_bin = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        python_bin = os.path.join(VENV_DIR, "bin", "python")
        pip_bin = os.path.join(VENV_DIR, "bin", "pip")
    if args[0] == "python":
        args[0] = python_bin
    elif args[0] == "pip":
        args[0] = pip_bin
    return subprocess.check_call(args)

def install_deps():
    print("[ETAPE] Installation/MAJ de pip...")
    run_in_venv(["python", "-m", "pip", "install", "--upgrade", "pip"])
    print("[ETAPE] Installation des dépendances...")
    run_in_venv(["pip", "install"] + REQUIREMENTS)
    print("[OK] Dépendances installées.")

def clean_build():
    print("[ETAPE] Nettoyage des anciens builds...")
    for d in [DIST_DIR, os.path.join(BUILD_DIR, "temp")]:
        if os.path.exists(d):
            shutil.rmtree(d)
    if os.path.exists(BUILD_DIR):
        for f in os.listdir(BUILD_DIR):
            if f.endswith(".spec"):
                os.remove(os.path.join(BUILD_DIR, f))
    os.makedirs(DIST_DIR, exist_ok=True)
    os.makedirs(os.path.join(BUILD_DIR, "temp"), exist_ok=True)
    print("[OK] Répertoires de build prêts.")

def build_exe():
    print("[ETAPE] Génération de l'exécutable...")
    pyinstaller_args = [
        "python", "-m", "PyInstaller",
        "--onefile", "--windowed",
        "--name", "CrazyTerm",
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(BUILD_DIR, "temp"),
        "--specpath", "build",
        "--noconsole",
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "PyQt5.QtWidgets",
        "--hidden-import", "serial",
    ]
    if os.path.exists(ICON_PATH):
        pyinstaller_args += ["--icon", ICON_PATH]
    pyinstaller_args.append(MAIN_SCRIPT)
    run_in_venv(pyinstaller_args)
    print("[OK] Exécutable généré.")

def purge_build():
    print("[ETAPE] Purge du dossier build...")
    for f in os.listdir(BUILD_DIR):
        path = os.path.join(BUILD_DIR, f)
        if os.path.isfile(path) and not f.lower().endswith(('.bat', '.md', '.py')):
            os.remove(path)
        elif os.path.isdir(path) and f != '__pycache__':
            shutil.rmtree(path)
    print("[OK] Dossier build purgé (seuls les scripts utiles sont conservés).")

def main():
    print("\n=== INSTALLATION AUTONOME CRAZYTERM ===\n")
    check_python_version()
    create_venv()
    install_deps()
    clean_build()
    build_exe()
    purge_build()
    print("\n=== INSTALLATION TERMINEE AVEC SUCCES ! ===\n")
    print(f"- Exécutable : {os.path.join(DIST_DIR, 'CrazyTerm.exe')}\n")
    print("Attention : Pour des raisons de sécurité (antivirus Windows), l'exécutable généré ne fonctionnera de façon fiable que sur ce PC. Pour une distribution sur d'autres machines, il est recommandé de re-générer l'exécutable sur chaque poste cible.")

if __name__ == "__main__":
    main()
