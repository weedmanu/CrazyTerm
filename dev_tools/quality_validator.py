#!/usr/bin/env python3
"""
Script de validation pour CrazyTerm - Version Simple et Efficace

Ce script audite la qualité, l'architecture et la performance du projet CrazyTerm.
Il applique des critères stricts sur chaque axe qualité (documentation, type hints, gestion d'erreur, etc.)
L'objectif est d'obtenir 100% sur chaque critère, avec un reporting vertical et lisible des fichiers non conformes.

Usage :
    python dev_tools/quality_validator.py

Sortie :
    Affiche les scores détaillés et la liste des fichiers à corriger pour chaque critère.
"""

import os
import sys
from typing import Optional, List, Dict, Any
import ast

class QualityValidator:
    """
    Classe principale pour la validation de la qualité, de l'architecture et des performances du projet CrazyTerm.
    Toutes les méthodes de validation sont des méthodes de classe.
    """

    @staticmethod
    def find_project_root(filename: str = "crazyterm.py") -> Optional[str]:
        current: str = os.path.abspath(os.getcwd())
        root: Optional[str] = None
        while True:
            if os.path.exists(os.path.join(current, filename)):
                root = current
                break
            parent: str = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        return root

    @classmethod
    def validate_code_quality(cls) -> float:
        print("\n=== [VALIDATION QUALITÉ DU CODE] ===\n")
        if not os.path.exists('crazyterm.py'):
            print("❌ Script non exécuté depuis le répertoire racine du projet")
            print("   Veuillez exécuter depuis le répertoire contenant crazyterm.py")
            return 0

        # --- Définition des cibles pertinentes pour chaque critère ---
        metrics_targets: Dict[str, List[str]] = {
            'error_handling': [
                'core/main_window.py', 'core/config_manager.py',
                'system/memory_optimizer.py', 'system/utilities.py',
                'system/error_handling.py', 'system/custom_exceptions.py',
                'tools/tool_converter.py', 'tools/tool_checksum.py',
                'interface/interface_components.py', 'interface/theme_manager.py',
                'communication/serial_communication.py'
            ],
            'logging': [
                'core/main_window.py', 'core/config_manager.py',
                'system/memory_optimizer.py', 'system/utilities.py',
                'system/error_handling.py', 'system/custom_exceptions.py',
                'tools/tool_converter.py', 'tools/tool_checksum.py',
                'interface/interface_components.py', 'interface/theme_manager.py',
                'communication/serial_communication.py'
            ],
            'type_hints': [
                'core/main_window.py', 'core/config_manager.py',
                'system/memory_optimizer.py', 'system/utilities.py',
                'system/error_handling.py', 'system/custom_exceptions.py',
                'tools/tool_converter.py', 'tools/tool_checksum.py',
                'interface/interface_components.py', 'interface/theme_manager.py',
                'communication/serial_communication.py'
            ],
            'documentation': [
                'core/main_window.py', 'core/config_manager.py',
                'system/memory_optimizer.py', 'system/utilities.py',
                'system/error_handling.py', 'system/custom_exceptions.py',
                'tools/tool_converter.py', 'tools/tool_checksum.py',
                'interface/interface_components.py', 'interface/theme_manager.py',
                'communication/serial_communication.py'
            ],
            'class_structure': [
                'core/main_window.py', 'core/config_manager.py',
                'system/memory_optimizer.py', 'system/utilities.py',
                'tools/tool_converter.py', 'tools/tool_checksum.py',
                'interface/interface_components.py', 'communication/serial_communication.py'
            ],
            'imports_optimization': [
                'core/main_window.py', 'core/config_manager.py',
                'system/memory_optimizer.py', 'system/utilities.py',
                'system/error_handling.py', 'system/custom_exceptions.py',
                'tools/tool_converter.py', 'tools/tool_checksum.py',
                'interface/interface_components.py', 'interface/theme_manager.py',
                'communication/serial_communication.py'
            ],
            'code_organization': [
                'core/main_window.py', 'core/config_manager.py',
                'system/memory_optimizer.py', 'system/utilities.py',
                'tools/tool_converter.py', 'tools/tool_checksum.py',
                'interface/interface_components.py', 'communication/serial_communication.py'
            ],
        }

        # --- Collecte des fichiers Python métiers ---
        python_files: List[str] = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if (file.endswith('.py') and 
                    not file.startswith('test_') and 
                    not file.startswith('validate_') and
                    not file.startswith('check_') and
                    not file.startswith('quality_') and
                    file != '__init__.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)

        # --- Initialisation des résultats ---
        results: Dict[str, Dict[str, Any]] = {}
        for metric, targets in metrics_targets.items():
            results[metric] = {
                'conformes': 0,
                'non_conformes': [],
                'total': len(targets)
            }

        # --- Analyse AST stricte par critère ---
        for metric, targets in metrics_targets.items():
            for rel_path_norm in targets:
                file_path = os.path.normpath(rel_path_norm)
                if not os.path.exists(file_path):
                    results[metric]['non_conformes'].append(f"{rel_path_norm} (absent)")
                    continue
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    tree = ast.parse(content)
                    # Analyse par critère
                    if metric == 'error_handling':
                        has_try = any(isinstance(node, ast.Try) for node in ast.walk(tree))
                        has_except = any(isinstance(node, ast.ExceptHandler) for node in ast.walk(tree))
                        has_raise = any(isinstance(node, ast.Raise) for node in ast.walk(tree))
                        if has_try and has_except and has_raise:
                            results[metric]['conformes'] += 1
                        else:
                            results[metric]['non_conformes'].append(rel_path_norm)
                    elif metric == 'logging':
                        has_logger = False
                        has_log_call = False
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Assign):
                                for target in node.targets:
                                    if isinstance(target, ast.Name) and target.id == 'logger':
                                        if isinstance(node.value, ast.Call):
                                            func = node.value.func
                                            if isinstance(func, ast.Attribute):
                                                if isinstance(func.value, ast.Name) and func.value.id == 'logging' and func.attr == 'getLogger':
                                                    has_logger = True
                            if isinstance(node, ast.Call):
                                func = node.func
                                if isinstance(func, ast.Attribute):
                                    if isinstance(func.value, ast.Name) and func.value.id == 'logger':
                                        if func.attr in ('info', 'error', 'warning', 'debug'):
                                            has_log_call = True
                        if has_logger and has_log_call:
                            results[metric]['conformes'] += 1
                        else:
                            results[metric]['non_conformes'].append(rel_path_norm)
                    elif metric == 'type_hints':
                        has_typing = 'from typing import' in content
                        all_annotated = True
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                if node.name in ('__init__', '__new__'):
                                    if any(arg.annotation is None for arg in node.args.args if arg.arg not in ('self', 'cls')):
                                        all_annotated = False
                                        break
                                else:
                                    if node.returns is None:
                                        all_annotated = False
                                        break
                                    if any(arg.annotation is None for arg in node.args.args if arg.arg not in ('self', 'cls')):
                                        all_annotated = False
                                        break
                                    if node.args.vararg and node.args.vararg.annotation is None:
                                        all_annotated = False
                                        break
                                    if node.args.kwarg and node.args.kwarg.annotation is None:
                                        all_annotated = False
                                        break
                        if has_typing and all_annotated:
                            results[metric]['conformes'] += 1
                        else:
                            results[metric]['non_conformes'].append(rel_path_norm)
                    elif metric == 'documentation':
                        has_module_doc = ast.get_docstring(tree) is not None
                        missing_class = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and not ast.get_docstring(node)]
                        missing_func = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node)]
                        has_class_doc = not missing_class
                        has_func_doc = not missing_func
                        if has_module_doc and has_class_doc and has_func_doc:
                            results[metric]['conformes'] += 1
                        else:
                            msg = rel_path_norm
                            if not has_module_doc:
                                msg += " [module sans docstring]"
                            if missing_class:
                                msg += f" [classes sans docstring: {missing_class}]"
                            if missing_func:
                                msg += f" [fonctions sans docstring: {missing_func}]"
                            results[metric]['non_conformes'].append(msg)
                    elif metric == 'class_structure':
                        has_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
                        has_method = any(
                            isinstance(node, ast.FunctionDef) and getattr(node, 'name', None) != '__init__'
                            for node in ast.walk(tree)
                        )
                        if has_class and has_method:
                            results[metric]['conformes'] += 1
                        else:
                            results[metric]['non_conformes'].append(rel_path_norm)
                    elif metric == 'imports_optimization':
                        if 'from __future__ import annotations' in content:
                            results[metric]['conformes'] += 1
                        else:
                            results[metric]['non_conformes'].append(rel_path_norm)
                    elif metric == 'code_organization':
                        if 'def ' in content and '__all__' not in content:
                            results[metric]['non_conformes'].append(rel_path_norm)
                        else:
                            results[metric]['conformes'] += 1
                except Exception as e:
                    results[metric]['non_conformes'].append(f"{rel_path_norm} (erreur: {e})")

        # --- Affichage des résultats détaillés ---
        print("\n=== Résultats détaillés de la validation ===")
        percs: List[float] = []
        for metric, data in results.items():
            total = data['total']
            conformes = data['conformes']
            non_conformes = data['non_conformes']
            score = (conformes / total) * 100 if total else 0.0
            percs.append(score)
            print(f"[OK] {metric} : {conformes}/{total} fichiers conformes ({score:.1f}%)")
            if non_conformes:
                print("   Fichiers non conformes :")
                for file in non_conformes:
                    print(f"    - {file}")
        # --- Score global ---
        global_score = sum(percs) / len(percs) if percs else 0.0
        print(f"\n[SCORE GLOBAL QUALITÉ] : {global_score:.1f}%")
        return global_score

    @classmethod
    def validate_robustness(cls) -> float:
        """
        Teste dynamiquement la robustesse du code (gestion d'erreur, retry, circuit breaker).
        Retourne un score sur 100.
        """
        import sys, os
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        print("\n=== [VALIDATION ROBUSTESSE] ===\n")
        score = 0
        total = 3
        ok = 0
        # Test retry_with_backoff
        try:
            from system.error_handling import retry_with_backoff
            calls = {'count': 0}
            @retry_with_backoff(max_retries=2, initial_delay=0.01)
            def fail_func():
                calls['count'] += 1
                raise ValueError('fail')
            try:
                fail_func()
            except ValueError:
                pass
            if calls['count'] == 3:
                print("[OK] retry_with_backoff fonctionne (3 tentatives)")
                ok += 1
            else:
                print("❌ retry_with_backoff ne fonctionne pas")
        except Exception as e:
            print(f"❌ retry_with_backoff erreur: {e}")
        # Test CircuitBreaker via call()
        try:
            from system.error_handling import CircuitBreaker
            cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
            def always_fail():
                raise RuntimeError('fail')
            for _ in range(2):
                try:
                    cb.call(always_fail)
                except Exception:
                    pass
            if cb.state == 'OPEN':
                print("[OK] CircuitBreaker fonctionne (passe en OPEN)")
                ok += 1
            else:
                print("❌ CircuitBreaker ne passe pas en OPEN")
        except Exception as e:
            print(f"❌ CircuitBreaker erreur: {e}")
        # Test safe_execute
        try:
            from system.error_handling import safe_execute
            res = safe_execute(lambda: 1/0, default_value=42)
            if res == 42:
                print("[OK] safe_execute fonctionne (retourne valeur par défaut)")
                ok += 1
            else:
                print("❌ safe_execute ne retourne pas la valeur par défaut")
        except Exception as e:
            print(f"❌ safe_execute erreur: {e}")
        score = (ok / total) * 100
        print(f"\n[SCORE ROBUSTESSE] : {score:.1f}%")
        return score

    @classmethod
    def validate_performance(cls) -> float:
        """
        Teste la performance de fonctions critiques (temps d'exécution).
        Retourne un score sur 100.
        """
        import sys, os
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        print("\n=== [VALIDATION PERFORMANCE] ===\n")
        import time
        total = 2
        ok = 0
        # Test rapidité resource_path
        try:
            from system.utilities import UtilityFunctions
            t0 = time.time()
            for _ in range(1000):
                UtilityFunctions.resource_path('assets/CrazyTerm.ico')
            t1 = time.time()
            duration = t1 - t0
            if duration < 0.5:
                print(f"[OK] resource_path rapide ({duration:.3f}s pour 1000 appels)")
                ok += 1
            else:
                print(f"❌ resource_path lent ({duration:.3f}s)")
        except Exception as e:
            print(f"❌ resource_path erreur: {e}")
        # Test import et instanciation Terminal
        try:
            from PyQt5.QtWidgets import QApplication
            import sys
            app = QApplication.instance() or QApplication(sys.argv)
            t0 = time.time()
            from core.main_window import Terminal
            _ = Terminal()  # instanciation, suppression de l'avertissement unused
            t1 = time.time()
            duration = t1 - t0
            if duration < 1.0:
                print(f"[OK] Instanciation Terminal rapide ({duration:.3f}s)")
                ok += 1
            else:
                print(f"❌ Instanciation Terminal lente ({duration:.3f}s)")
            app.quit()
        except Exception as e:
            print(f"❌ Instanciation Terminal erreur: {e}")
        score = (ok / total) * 100
        print(f"\n[SCORE PERFORMANCE] : {score:.1f}%")
        return score

if __name__ == "__main__":
    root_dir = QualityValidator.find_project_root()
    if root_dir:
        os.chdir(root_dir)
        print(f"[OK] Répertoire racine du projet trouvé : {root_dir}")
    else:
        print("❌ Répertoire racine du projet non trouvé. Veuillez exécuter depuis le répertoire contenant crazyterm.py")
        sys.exit(1)
    score_quality = QualityValidator.validate_code_quality()
    score_robust = QualityValidator.validate_robustness()
    score_perf = QualityValidator.validate_performance()
    print("\n=== [RÉCAPITULATIF GLOBAL] ===")
    print(f"Qualité statique : {score_quality:.1f}%")
    print(f"Robustesse       : {score_robust:.1f}%")
    print(f"Performance      : {score_perf:.1f}%")
    global_score = (score_quality + score_robust + score_perf) / 3
    print(f"\n[SCORE GLOBAL] : {global_score:.1f}%")
    if global_score == 100:
        print("Bravo ! Le code respecte toutes les exigences de qualité, robustesse et performance.")
    elif global_score >= 80:
        print("Bon travail ! Le code est de bonne qualité, mais quelques améliorations sont possibles.")
    elif global_score >= 50:
        print("Attention : Le code présente des problèmes qui doivent être corrigés.")
    else:
        print("Mauvaise qualité détectée. Des corrections majeures sont nécessaires.")
