#!/usr/bin/env python3
"""
Potaria - Exhaustive Pygame-CE to Unity 6 LTS Feature Parity Documentation Generator
Developer: Kurados
Generates docs/PYGAME_TO_UNITY_FEATURE_PARITY_DOCUMENTATION.md
Strict constraints:
- NO emojis
- NO local machine file paths (use relative repository paths)
- Exhaustive inventory of all 65 Python files, 123 classes, 1170 methods, 153 functions
- Master numeric tables, formulas, pseudo-code, and parity matrix
"""

import os
import sys
import json
import ast
import glob
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITY_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PYGAME_DIR = os.path.abspath(os.path.join(UNITY_DIR, "..", "Potaria_Pygame_Backup"))
OUTPUT_FILE = os.path.join(UNITY_DIR, "docs", "PYGAME_TO_UNITY_FEATURE_PARITY_DOCUMENTATION.md")

def get_ast_inventory():
    py_files = [os.path.join(PYGAME_DIR, "main.py")] + sorted(glob.glob(os.path.join(PYGAME_DIR, "src", "**", "*.py"), recursive=True))
    inventory = []
    for fpath in py_files:
        rel = os.path.relpath(fpath, PYGAME_DIR).replace("\\", "/")
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            continue

        file_doc = ast.get_docstring(tree) or ""
        lines = len(content.splitlines())
        size_bytes = len(content.encode("utf-8"))

        classes = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                c_doc = ast.get_docstring(node) or ""
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        m_doc = ast.get_docstring(item) or ""
                        args = []
                        for a in item.args.args:
                            args.append(a.arg)
                        methods.append({
                            "name": item.name,
                            "args": args,
                            "doc": m_doc.strip().split("\n")[0] if m_doc else "",
                            "lineno": item.lineno
                        })
                classes.append({
                    "name": node.name,
                    "doc": c_doc.strip().split("\n")[0] if c_doc else "",
                    "methods": methods,
                    "lineno": node.lineno
                })

        functions = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                f_doc = ast.get_docstring(node) or ""
                args = [a.arg for a in node.args.args]
                functions.append({
                    "name": node.name,
                    "args": args,
                    "doc": f_doc.strip().split("\n")[0] if f_doc else "",
                    "lineno": node.lineno
                })

        inventory.append({
            "path": rel,
            "lines": lines,
            "bytes": size_bytes,
            "doc": file_doc.strip().split("\n")[0] if file_doc else "",
            "classes": classes,
            "functions": functions
        })
    return inventory

if __name__ == "__main__":
    inv = get_ast_inventory()
    print(f"Loaded {len(inv)} files for inventory.")
