#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
venv_manager.py - Gestionnaire robuste d'environnement virtuel pour CrazyTerm

Fonctionnalités :
- Suppression forcée du venv existant
- Création d'un nouvel environnement virtuel
- Installation automatique des dépendances (requirements.txt, flake8, pylint)
- Détection et gestion de l'activation/désactivation du venv
- Ouverture automatique d'un shell avec le venv activé (Windows/Linux)
- Messages clairs et robustesse accrue

Usage :
    python dev_tools/venv_manager.py [reset|create|delete|activate|status]

Par défaut : reset complet (suppression + création + activation)
"""
import os
import shutil
import subprocess
import sys
import platform
import stat
import ctypes
from typing import Callable, Any

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VENV_DIR = os.path.join(ROOT, '.venv')
REQUIREMENTS = os.path.join(ROOT, 'dev_tools', 'requirements.txt')

# Utilitaires

def on_rm_error(func: Callable[[str], Any], path: str, exc_info: Any) -> None:
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"[WARN] Impossible de supprimer {path} : {e}")

def venv_active():
    return bool(os.environ.get('VIRTUAL_ENV'))

def pip_python_paths():
    if platform.system() == "Windows":
        pip_path = os.path.join(VENV_DIR, 'Scripts', 'pip.exe')
        python_path = os.path.join(VENV_DIR, 'Scripts', 'python.exe')
    else:
        pip_path = os.path.join(VENV_DIR, 'bin', 'pip')
        python_path = os.path.join(VENV_DIR, 'bin', 'python')
    return pip_path, python_path

def delete_venv():
    if os.path.isdir(VENV_DIR):
        print(f"[INFO] Suppression de l'environnement virtuel : {VENV_DIR}")
        shutil.rmtree(VENV_DIR, onerror=on_rm_error)
        print("[OK] .venv supprimé.")
    else:
        print("[INFO] Aucun environnement virtuel .venv à supprimer.")

def create_venv():
    print("[INFO] Création du nouvel environnement virtuel...")
    for tentative in range(2):
        try:
            subprocess.check_call([sys.executable, '-m', 'venv', VENV_DIR])
        except subprocess.CalledProcessError as e:
            print(f"[ERREUR] La commande de création du venv a échoué : {e}")
            if tentative == 1:
                sys.exit(1)
        pyvenv_cfg = os.path.join(VENV_DIR, 'pyvenv.cfg')
        if os.path.isfile(pyvenv_cfg):
            print("[OK] .venv créé.")
            return
        else:
            print(f"[WARN] Le fichier pyvenv.cfg est introuvable dans {VENV_DIR}.")
            print("[INFO] Suppression automatique du dossier .venv corrompu et nouvelle tentative...")
            if os.path.isdir(VENV_DIR):
                shutil.rmtree(VENV_DIR, onerror=on_rm_error)
    print(f"[ERREUR] Impossible de créer un environnement virtuel fonctionnel dans {VENV_DIR} après 2 tentatives.")
    print("[CONSEIL] Vérifiez vos droits d'écriture, la version de Python et l'espace disque.")
    sys.exit(1)

def install_deps():
    pip_path, python_path = pip_python_paths()
    print(f"[INFO] Installation des dépendances du projet et de développement dans le venv...")
    try:
        print(f"[DEBUG] Upgrade pip: {python_path} -m pip install --upgrade pip")
        subprocess.check_call([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'])
        # Installation requirements.txt
        if os.path.isfile(REQUIREMENTS):
            print(f"[DEBUG] Install requirements: {pip_path} install -r {REQUIREMENTS}")
            subprocess.check_call([pip_path, 'install', '-r', REQUIREMENTS])
            print(f"[OK] requirements.txt installé dans le venv.")
        else:
            print("[WARN] Aucun requirements.txt trouvé.")
        # Installation dev_requirements.txt (dans dev_tools)
        dev_req = os.path.join(ROOT, 'dev_tools', 'dev_requirements.txt')
        if os.path.isfile(dev_req):
            print(f"[DEBUG] Install dev_requirements: {pip_path} install -r {dev_req}")
            subprocess.check_call([pip_path, 'install', '-r', dev_req])
            print(f"[OK] dev_requirements.txt installé dans le venv.")
        else:
            print("[INFO] Installation de flake8 et pylint (dépendances de base dev)")
            subprocess.check_call([pip_path, 'install', 'flake8', 'pylint'])
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] L'installation des dépendances a échoué : {e}")
        if hasattr(e, 'output') and e.output:
            print(e.output)
        sys.exit(2)

def activate_venv():
    pip_path, python_path = pip_python_paths()
    if platform.system() == "Windows":
        activate_cmd = os.path.join(ROOT, '.venv', 'Scripts', 'Activate.ps1')
        print("[INFO] Ouverture d'une nouvelle fenêtre PowerShell avec le venv activé...")
        ctypes.windll.user32.MessageBoxW(0, "Une nouvelle fenêtre PowerShell va s'ouvrir avec le venv activé.", "Activation venv", 0)
        subprocess.Popen(["powershell.exe", "-NoExit", "-Command", f". '{activate_cmd}'"])
    else:
        activate_cmd = os.path.join(ROOT, '.venv', 'bin', 'activate')
        print("[INFO] Ouverture d'un nouveau terminal bash avec le venv activé...")
        subprocess.Popen(["x-terminal-emulator", "-e", f"bash --rcfile {activate_cmd}"])
    print(f"[OK] Shell ouvert. Pour utiliser le venv : {python_path} <votre_script.py>")

def status_venv():
    _, python_path = pip_python_paths()
    pip_path, _ = pip_python_paths()
    print(f"[INFO] Statut de l'environnement virtuel :")
    print(f"  Présent : {'Oui' if os.path.isdir(VENV_DIR) else 'Non'}")
    print(f"  Actif  : {'Oui' if venv_active() else 'Non'}")
    print(f"  Python : {python_path if os.path.exists(python_path) else 'Non trouvé'}")
    print(f"  Pip    : {pip_path if os.path.exists(pip_path) else 'Non trouvé'}")

# Commandes principales

def main():
    try:
        cmd = sys.argv[1] if len(sys.argv) > 1 else 'reset'
        print(f"[INFO] Commande demandée : {cmd}")
        venv_env = os.environ.get('VIRTUAL_ENV')
        if venv_env:
            if os.path.abspath(venv_env) == os.path.abspath(VENV_DIR):
                print(f"[ERREUR] Vous exécutez ce script depuis le venv du projet : {venv_env}\n")
                print("[BLOCAGE] Il est impossible de réinitialiser le venv depuis une session où il est actif.")
                print("Ouvrez un nouveau terminal (PowerShell ou CMD sous Windows, bash sous Linux) sans activer le venv, puis relancez :\n")
                print("    python dev_tools/venv_manager.py reset\n")
                print("Astuce : Fermez ce terminal, ouvrez-en un nouveau, et vérifiez que le prompt ne contient pas .venv avant de relancer la commande.")
                sys.exit(1)
            else:
                print(f"[AVERTISSEMENT] Un environnement virtuel est actif : {venv_env}\nIl est recommandé de désactiver tout venv avant d'utiliser ce script pour éviter les conflits.")
                print("Pour forcer l'exécution, relancez avec l'option --force (non recommandé sauf cas expert).\n")
                if '--force' not in sys.argv:
                    sys.exit(1)
        if cmd == 'reset':
            delete_venv()
            create_venv()
            install_deps()
            activate_venv()
        elif cmd == 'delete':
            delete_venv()
        elif cmd == 'create':
            create_venv()
            install_deps()
        elif cmd == 'activate':
            activate_venv()
        elif cmd == 'status':
            status_venv()
        else:
            print("Usage : python dev_tools/venv_manager.py [reset|create|delete|activate|status] [--force]")
            sys.exit(1)
        print("\n[OK] Opération terminée.")
    except Exception as e:
        print(f"[ERREUR] Exception inattendue : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()
