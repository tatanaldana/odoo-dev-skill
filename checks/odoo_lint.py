#!/usr/bin/env python3
"""Deterministic pre-check for odoo-dev-skill.

Catches the subset of CRITICAL/HIGH rules from SKILL.md and
agents/odoo-coding-guidelines-validator.md that are mechanically detectable
(raw SQL, attrs=, manual commit/rollback, missing ensure_one, etc.) so the
review agents don't rely purely on the model remembering to check for them.

Stdlib only — no dependencies. Works on a single file or a directory tree.

Usage:
    python3 checks/odoo_lint.py <path> [--odoo-version 18] [--format text|json]

Exit code is always 0 — this is a pre-check to feed into an LLM review, not a
CI gate. Findings are heuristics: verify before treating them as confirmed.
"""

import argparse
import ast
import csv
import io
import json
import os
import re
import sys

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".claude"}


def iter_files(path, exts):
    if os.path.isfile(path):
        if os.path.splitext(path)[1] in exts:
            yield path
        return
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1] in exts:
                yield os.path.join(root, f)


def finding(rule_id, severity, file, line, message):
    return {
        "rule": rule_id,
        "severity": severity,
        "file": file,
        "line": line,
        "message": message,
    }


# ---------------------------------------------------------------------------
# Python checks (AST-based)
# ---------------------------------------------------------------------------

def _is_cr_execute(call):
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "execute"
        and isinstance(call.func.value, ast.Attribute)
        and call.func.value.attr == "cr"
    )


def _is_cr_commit_or_rollback(call):
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr in ("commit", "rollback")
        and isinstance(call.func.value, ast.Attribute)
        and call.func.value.attr == "cr"
    )


def check_python(path, source, findings):
    lines = source.splitlines()
    if lines and re.search(r"coding[:=]\s*utf-8", lines[0] + (lines[1] if len(lines) > 1 else "")):
        findings.append(finding(
            "CS-02", "HIGH", path, 1,
            "Remove `# -*- coding: utf-8 -*-` header — not needed in Python 3.",
        ))

    if re.search(r"^\s*print\(", source, re.MULTILINE):
        for i, l in enumerate(lines, 1):
            if re.match(r"^\s*print\(", l):
                findings.append(finding(
                    "LOG-01", "MEDIUM", path, i,
                    "Use `_logger.info/warning/error` instead of `print()`.",
                ))

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as e:
        findings.append(finding(
            "PARSE", "INFO", path, e.lineno or 1,
            f"Could not parse file for AST checks: {e.msg}",
        ))
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "super" and len(node.args) >= 1:
                findings.append(finding(
                    "CS-03", "HIGH", path, node.lineno,
                    "Use `super()` without arguments, not `super(ClassName, self)`.",
                ))

            if _is_cr_commit_or_rollback(node):
                findings.append(finding(
                    "TX-01", "CRITICAL", path, node.lineno,
                    "Manual cr.commit()/cr.rollback() — let the ORM transaction handle this.",
                ))

            if _is_cr_execute(node):
                findings.append(finding(
                    "OI-01", "HIGH", path, node.lineno,
                    "Raw SQL via cr.execute() — verify the ORM (search/read_group/filtered) can't do this instead.",
                ))
                segment = ast.get_source_segment(source, node) or ""
                if re.search(r'f["\']', segment) or ".format(" in segment or re.search(r'["\'].*\+.*\w', segment):
                    findings.append(finding(
                        "SEC-03", "CRITICAL", path, node.lineno,
                        "Possible SQL injection: cr.execute() built via f-string/.format()/concatenation instead of parameterized query.",
                    ))

        if isinstance(node, ast.For):
            for inner in _walk_body(node.body):
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr in ("browse", "search"):
                    findings.append(finding(
                        "OI-02", "HIGH", path, inner.lineno,
                        f"`.{inner.func.attr}()` call inside a for-loop — verify it isn't an N+1 query; prefer mapped()/filtered() or a single search() before the loop.",
                    ))

        if isinstance(node, ast.FunctionDef) and node.name.startswith("action_"):
            body = [s for s in node.body if not (isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant) and isinstance(s.value.value, str))]
            has_ensure_one_first = bool(body) and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Call) and isinstance(body[0].value.func, ast.Attribute) and body[0].value.func.attr == "ensure_one"
            has_ensure_one_anywhere = any(
                isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "ensure_one"
                for n in ast.walk(node)
            )
            if not has_ensure_one_anywhere:
                findings.append(finding(
                    "NP-04", "HIGH", path, node.lineno,
                    f"`{node.name}` is missing `self.ensure_one()`.",
                ))
            elif not has_ensure_one_first:
                findings.append(finding(
                    "NP-04", "MEDIUM", path, node.lineno,
                    f"`{node.name}` calls ensure_one() but not as the first statement.",
                ))


def _walk_body(stmts):
    """ast.walk over a list of statements (ast.walk only accepts a single node)."""
    for s in stmts:
        yield from ast.walk(s)


# ---------------------------------------------------------------------------
# XML checks (regex — stdlib ElementTree doesn't track line numbers cheaply)
# ---------------------------------------------------------------------------

def check_xml(path, source, findings, odoo_version):
    for i, line in enumerate(source.splitlines(), 1):
        if re.search(r'\battrs\s*=\s*["\']', line):
            findings.append(finding(
                "XV-04", "CRITICAL", path, i,
                "`attrs=` is removed in v17+ — use `invisible=`/`readonly=`/`required=` directly.",
            ))
        if odoo_version and odoo_version >= 18 and re.search(r"<tree\b", line):
            findings.append(finding(
                "XV-06", "MEDIUM", path, i,
                "`<tree>` is renamed to `<list>` from Odoo 18 onward.",
            ))
        if re.search(r'src\s*=\s*["\']https?://', line) or re.search(r'href\s*=\s*["\']https?://', line):
            findings.append(finding(
                "XV-05", "MEDIUM", path, i,
                "External URL for a static resource — copy it into the module's static/ directory instead.",
            ))


# ---------------------------------------------------------------------------
# Cross-file check: every new model needs an ir.model.access.csv entry
# ---------------------------------------------------------------------------

def check_access_rights(root, findings):
    if os.path.isfile(root):
        return

    model_defs = []  # (model_name, file, line)
    model_name_re = re.compile(r"^\s*_name\s*=\s*['\"]([\w.]+)['\"]")
    for py_file in iter_files(root, {".py"}):
        try:
            with open(py_file, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    m = model_name_re.match(line)
                    if m:
                        model_defs.append((m.group(1), py_file, i))
        except (OSError, UnicodeDecodeError):
            continue

    if not model_defs:
        return

    csv_content = ""
    for csv_file in iter_files(root, {".csv"}):
        if "access" not in os.path.basename(csv_file):
            continue
        try:
            with open(csv_file, encoding="utf-8") as f:
                csv_content += f.read()
        except (OSError, UnicodeDecodeError):
            continue

    for model_name, file, line in model_defs:
        token = "model_" + model_name.replace(".", "_")
        if token not in csv_content:
            findings.append(finding(
                "SEC-01", "CRITICAL", file, line,
                f"No ir.model.access.csv entry found for model `{model_name}` (expected a row referencing `{token}`).",
            ))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(path, odoo_version):
    findings = []

    for py_file in iter_files(path, {".py"}):
        try:
            with open(py_file, encoding="utf-8") as f:
                source = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        check_python(py_file, source, findings)

    for xml_file in iter_files(path, {".xml"}):
        try:
            with open(xml_file, encoding="utf-8") as f:
                source = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        check_xml(xml_file, source, findings, odoo_version)

    check_access_rights(path, findings)

    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f["file"], f["line"]))
    return findings


def render_text(findings):
    if not findings:
        return "No static findings. This does not replace a full guidelines review — it only covers mechanically-detectable rules."

    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "INFO": 0}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    out = io.StringIO()
    out.write("## Static Check Report (checks/odoo_lint.py)\n\n")
    out.write("| Severity | Count |\n|---|---|\n")
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "INFO"):
        if counts.get(sev):
            out.write(f"| {sev} | {counts[sev]} |\n")
    out.write("\n")
    for f in findings:
        out.write(f"### [{f['severity']}] {f['rule']} — {f['file']}:{f['line']}\n")
        out.write(f"{f['message']}\n\n")
    out.write(
        "Note: these are heuristic, mechanically-detectable findings only. "
        "They do not replace the full LLM-driven guidelines review — merge "
        "them with it and verify before reporting as confirmed.\n"
    )
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="File or directory to scan")
    parser.add_argument("--odoo-version", type=int, default=None, help="Target Odoo major version (17, 18, 19...)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    findings = run(args.path, args.odoo_version)

    if args.format == "json":
        print(json.dumps(findings, indent=2))
    else:
        print(render_text(findings))

    return 0


if __name__ == "__main__":
    sys.exit(main())
