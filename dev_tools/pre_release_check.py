#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module : pre_build_check.py

Script d'automatisation de la pré-build CrazyTerm

Rôle :
    Vérifie les points clés avant la préparation du build logiciel.
    Complète quality_validator.py par des vérifications système, packaging et documentation.

Fonctionnalités principales :
    - Lancement du validateur qualité
    - Vérification des dépendances (obsolètes, sécurité)
    - Vérification de la documentation (README, CHANGELOG)
    - Vérification du packaging PyInstaller
    - Installation des dépendances
    - Reporting synthétique

Utilisation :
    python dev_tools/pre_build_check.py

Auteur :
    Projet CrazyTerm (2025) Manu
"""

import os
import sys
import subprocess

# Patch pour forcer l'encodage UTF-8 sur la sortie standard si nécessaire
if sys.stdout.encoding is not None and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass  # Pour compatibilité Python <3.7

def check_command(cmd: str, success_msg: str, fail_msg: str) -> bool:
    """
    Exécute une commande système et affiche un message selon le résultat.
    Retourne True si succès, False sinon.
    """
    try:
        _ = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ {success_msg}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {fail_msg}\n{e.stderr.decode(errors='ignore')}")
        return False

def main() -> None:
    """
    Exécute la checklist automatisée de pré-build pour CrazyTerm.
    """
    print("\n" + "="*60)
    print("{:^60}".format("CHECKLIST AUTOMATISÉE DE PRÉ-BUILD"))
    print("="*60)
    print()
    steps: list[tuple[str, bool]] = []
    all_ok: bool = True
    script_dir: str = os.path.dirname(os.path.abspath(__file__))
    project_root: str = os.path.abspath(os.path.join(script_dir, '..'))
    # 1. Qualité du code
    print("\n{:^60}\n".format("QUALITÉ DU CODE"))
    print("-"*60)
    quality_validator_path: str = os.path.join(script_dir, "quality_validator.py")
    ok = check_command(
        f"{sys.executable} {quality_validator_path}",
        "Tests quality_validator OK",
        "Tests quality_validator échoués"
    )
    steps.append(("Qualité du code", ok))
    all_ok &= ok
    # 2. Vérification dépendances à jour
    print("\n{:^60}\n".format("DÉPENDANCES (OBSOLESCENCE)"))
    print("-"*60)
    ok = check_command(
        f"{sys.executable} -m pip list --outdated",
        "Vérification des dépendances (obsolètes listées ci-dessus)",
        "Erreur lors de la vérification des dépendances"
    )
    steps.append(("Dépendances obsolètes", ok))
    all_ok &= ok
    # 3. Vérification sécurité (pip-audit)
    print("\n{:^60}\n".format("SÉCURITÉ DES DÉPENDANCES"))
    print("-"*60)
    ok = check_command(
        f"{sys.executable} -m pip install pip-audit",
        "pip-audit installé",
        "Erreur installation pip-audit"
    )
    all_ok &= ok
    ok2 = check_command(
        f"{sys.executable} -m pip_audit",
        "Audit sécurité pip-audit OK (voir ci-dessus)",
        "Vulnérabilités détectées ou erreur pip-audit"
    )
    steps.append(("Sécurité des dépendances", ok and ok2))
    all_ok &= ok2
    # 4. Vérification README et CHANGELOG
    print("\n{:^60}\n".format("DOCUMENTATION"))
    print("-"*60)
    docs_ok = True
    for doc in ["README.md", "CHANGELOG.md"]:
        doc_path: str = os.path.join(project_root, doc)
        if os.path.exists(doc_path):
            print(f"✅ {doc} présent")
        else:
            print(f"❌ {doc} manquant")
            docs_ok = False
    steps.append(("Documentation", docs_ok))
    all_ok &= docs_ok
    # 5. Vérification packaging PyInstaller
    print("\n{:^60}\n".format("PACKAGING (PyInstaller)"))
    print("-"*60)
    crazyterm_path: str = os.path.join(project_root, "crazyterm.py")
    packaging_ok = True
    if os.path.exists(crazyterm_path):
        ok = check_command(
            f"{sys.executable} -m pip install pyinstaller",
            "PyInstaller installé",
            "Erreur installation PyInstaller"
        )
        packaging_ok &= ok
        ok = check_command(
            f"{sys.executable} -m PyInstaller --noconfirm --onefile {crazyterm_path}",
            "Build PyInstaller OK",
            "Erreur lors du build PyInstaller"
        )
        packaging_ok &= ok
    else:
        print("❌ crazyterm.py introuvable pour le packaging")
        packaging_ok = False
    steps.append(("Packaging PyInstaller", packaging_ok))
    all_ok &= packaging_ok
    # 6. Installation des dépendances à partir de requirements.txt
    print("\n{:^60}\n".format("INSTALLATION DES DÉPENDANCES"))
    print("-"*60)
    requirements_path: str = os.path.join(project_root, "requirements.txt")
    req_ok = True
    if os.path.exists(requirements_path):
        ok = check_command(
            f"{sys.executable} -m pip install -r {requirements_path}",
            "Dépendances installées à partir de requirements.txt",
            "Erreur lors de l'installation des dépendances"
        )
        req_ok &= ok
    else:
        print("❌ requirements.txt introuvable")
        req_ok = False
    steps.append(("Installation des dépendances", req_ok))
    all_ok &= req_ok
    # 7. Purge du projet
    print("\n{:^60}\n".format("PURGE DU PROJET"))
    print("-"*60)
    purge_script = os.path.join(script_dir, "purge_project.py")
    purge_ok = False
    if os.path.exists(purge_script):
        purge_ok = check_command(
            f"{sys.executable} {purge_script}",
            "Purge projet OK",
            "Purge projet échouée"
        )
    else:
        print("❌ purge_project.py introuvable")
        purge_ok = False
    steps.append(("Purge projet", purge_ok))
    all_ok &= purge_ok
    # --- Récapitulatif global harmonisé ---
    print("\n" + "="*60)
    print("{:^60}".format("RÉCAPITULATIF GLOBAL"))
    print("="*60)
    for label, ok in steps:
        status = "✅" if ok else "❌"
        print(f"{status} {label}")
    print("-"*60)
    if all_ok:
        print("\n🎉 Tous les points critiques sont validés. Prêt pour le build ! 🎉\n")
    else:
        print("\n⚠️  Des points restent à corriger avant le build.\n")
    # --- Fin du rapport ---
    print("\n{:^60}\n".format("FIN DU RAPPORT"))

if __name__ == "__main__":
    main()
