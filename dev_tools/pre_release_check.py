#!/usr/bin/env python3
"""
Script d'automatisation de la pré-release CrazyTerm

Ce script vérifie les points clés avant la validation finale du logiciel.
Il complète quality_validator.py par des vérifications système, packaging et documentation.

Usage :
    python dev_tools/pre_release_check.py
"""
import os
import sys
import subprocess

def check_command(cmd, success_msg, fail_msg):
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ {success_msg}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {fail_msg}\n{e.stderr.decode(errors='ignore')}")
        return False

def main():
    print("\n=== CHECKLIST AUTOMATISÉE DE PRÉ-RELEASE ===\n")
    all_ok = True
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    # 1. Qualité du code
    quality_validator_path = os.path.join(script_dir, "quality_validator.py")
    all_ok &= check_command(
        f"{sys.executable} {quality_validator_path}",
        "Tests quality_validator OK",
        "Tests quality_validator échoués"
    )
    # 2. Vérification dépendances à jour
    all_ok &= check_command(
        f"{sys.executable} -m pip list --outdated",
        "Vérification des dépendances (obsolètes listées ci-dessus)",
        "Erreur lors de la vérification des dépendances"
    )
    # 3. Vérification sécurité (pip-audit)
    all_ok &= check_command(
        f"{sys.executable} -m pip install pip-audit",
        "pip-audit installé",
        "Erreur installation pip-audit"
    )
    all_ok &= check_command(
        f"{sys.executable} -m pip_audit",
        "Audit sécurité pip-audit OK (voir ci-dessus)",
        "Vulnérabilités détectées ou erreur pip-audit"
    )
    # 4. Vérification README et CHANGELOG
    for doc in ["README.md", "CHANGELOG.md"]:
        doc_path = os.path.join(project_root, doc)
        if os.path.exists(doc_path):
            print(f"[OK] {doc} présent")
        else:
            print(f"❌ {doc} manquant")
            all_ok = False
    # 5. Vérification packaging PyInstaller
    crazyterm_path = os.path.join(project_root, "crazyterm.py")
    if os.path.exists(crazyterm_path):
        all_ok &= check_command(
            f"{sys.executable} -m pip install pyinstaller",
            "PyInstaller installé",
            "Erreur installation PyInstaller"
        )
        all_ok &= check_command(
            f"{sys.executable} -m PyInstaller --noconfirm --onefile {crazyterm_path}",
            "Build PyInstaller OK",
            "Erreur lors du build PyInstaller"
        )
    else:
        print("❌ crazyterm.py introuvable pour le packaging")
        all_ok = False
    # 6. Installation des dépendances à partir de requirements.txt
    requirements_path = os.path.join(project_root, "requirements.txt")
    if os.path.exists(requirements_path):
        all_ok &= check_command(
            f"{sys.executable} -m pip install -r {requirements_path}",
            "Dépendances installées à partir de requirements.txt",
            "Erreur lors de l'installation des dépendances"
        )
    else:
        print("❌ requirements.txt introuvable")
        all_ok = False
    print("\n=== RÉCAPITULATIF ===")
    if all_ok:
        print("\nTous les points critiques sont validés. Prêt pour la release !")
    else:
        print("\nDes points restent à corriger avant la release.")

if __name__ == "__main__":
    main()
