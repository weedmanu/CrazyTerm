#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de réinitialisation de l'environnement virtuel CrazyTerm.
Supprime et recrée le dossier .venv à la racine du projet.
"""

import os
import shutil
import subprocess

venv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.venv'))

if os.path.exists(venv_path):
    print(f"Suppression de {venv_path} ...")
    shutil.rmtree(venv_path)

subprocess.check_call(['python', '-m', 'venv', venv_path])
print("Environnement virtuel recréé.")
