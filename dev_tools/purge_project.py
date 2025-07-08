#!/usr/bin/env python3
"""
Script de purge du projet CrazyTerm

Supprime tous les fichiers générés, temporaires, de build, logs, .pyc, __pycache__, dist, build, etc.
Usage :
    python dev_tools/purge_project.py
"""
import os
import shutil

# Extensions et dossiers à supprimer
PATTERNS = [
    '*.pyc', '*.pyo', '*.log', '*.tmp', '*.bak', '*.swp', '*.swo',
    '__pycache__', 'build', 'dist', '*.spec', '.pytest_cache', '.mypy_cache', '.coverage', '.DS_Store', '*.egg-info', '.venv', '.idea', '.vscode'
]

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

import fnmatch

def purge():
    print(f"Purge du projet dans : {ROOT}\n")
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Purge fichiers
        for pattern in PATTERNS:
            for filename in fnmatch.filter(filenames, pattern):
                path = os.path.join(dirpath, filename)
                try:
                    os.remove(path)
                    print(f"[DEL] {path}")
                except Exception as e:
                    pass
        # Purge dossiers
        for pattern in PATTERNS:
            for dirname in fnmatch.filter(dirnames, pattern):
                path = os.path.join(dirpath, dirname)
                try:
                    shutil.rmtree(path)
                    print(f"[DEL DIR] {path}")
                except Exception as e:
                    pass

if __name__ == "__main__":
    purge()
    print("\nPurge terminée.")
