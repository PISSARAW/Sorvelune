"""Contrôles bloquants sur un instantané Git isolé."""
import os
import re
import subprocess
import sys
from pathlib import Path

from python_rules import check as check_python

DOC_TREE = ("docs/README.md", "docs/architecture/README.md", "docs/guides/README.md",
            "docs/adr/README.md", "docs/adr/0001-gouvernance.md")
CODE = {".py", ".go", ".sh", ".js", ".jsx", ".ts", ".tsx", ".rs", ".c", ".h",
        ".cpp", ".java", ".sql", ".yml", ".yaml"}
ADR = re.compile(r"docs/adr/\d{4}-[a-z0-9-]+\.md")
MAJOR = {"go.mod", "pyproject.toml", "quality/check.py", "quality/python_rules.py",
         "quality/gate.sh", "quality/gocheck/main.go", ".github/workflows/quality.yml"}


def git_paths(args):
    data = subprocess.check_output(["git", *args, "-z"])
    return [os.fsdecode(item) for item in data.split(b"\0") if item]


def is_code(path):
    return Path(path).suffix in CODE or path.startswith(".githooks/") or Path(path).name == "Makefile"


def is_runtime(path):
    return is_code(path) and not (path.startswith("tests/") or Path(path).name.startswith("test_")
                                  or path.endswith("_test.go"))


def documentation(path):
    return path == "README.md" or (path.startswith("docs/") and path.endswith(".md"))


def declarations(message):
    fields = subprocess.check_output(["git", "interpret-trailers", "--parse"], input=message.encode())
    result = {}
    for line in fields.decode().splitlines():
        key, _, value = line.partition(":")
        if key in ("Impact", "Design-Review"):
            if key in result:
                raise ValueError(f"Déclaration dupliquée : {key}")
            result[key] = value.strip()
    return result


def major_path(path):
    return path in MAJOR or path.startswith(("schemas/", "migrations/", "docs/architecture/", ".githooks/"))


def valid_adr(path):
    text = path.read_text()
    for title in ("Contexte", "Options", "Décision", "Conséquences"):
        section = re.search(rf"^## {title}[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if not section or not section[1].strip():
            return False
    return True


def check_message(changed, tags):
    if not any(is_code(p) for p in changed):
        return
    if tags.get("Impact") not in {"mineur", "important", "majeur"}:
        raise ValueError("Message : préciser Impact: mineur, important ou majeur.")
    if tags.get("Design-Review") != "KISS, SOLID":
        raise ValueError("Message : attester la revue avec Design-Review: KISS, SOLID.")


def require_adr(root, refs):
    added = git_paths(["diff", "--no-renames", "--name-only", "--diff-filter=A", *refs])
    if not any(ADR.fullmatch(p) and valid_adr(root / p) for p in added):
        raise ValueError("Changement majeur : ajouter un ADR numéroté avec ses quatre sections.")


def updated_doc(root, path):
    return documentation(path) and (root / path).is_file() and (root / path).stat().st_size


def doc_policy(root, refs, tags):
    base, tree = refs
    changed = git_paths(["diff", "--no-renames", "--name-only", base, tree])
    written = git_paths(["diff", "--no-renames", "--name-only", "--diff-filter=AM", base, tree])
    major = tags.get("Impact") == "majeur" or any(map(major_path, changed))
    created_removed = git_paths(["diff", "--no-renames", "--name-only", "--diff-filter=AD", base, tree])
    important = major or tags.get("Impact") == "important" or any(map(is_runtime, created_removed))
    if important and not any(updated_doc(root, p) for p in written):
        raise ValueError("Modification importante : inclure une mise à jour du README ou de docs/.")
    if major:
        require_adr(root, refs)
    if (root.parent / "message").exists():
        check_message(changed, tags)


def source_checks(root, path):
    file = root / path
    if file.is_symlink():
        raise ValueError(f"{path} : fichier de code symbolique")
    text = file.read_text(encoding="utf-8")
    lines = len(text.splitlines())
    if lines > 500:
        return [f"{path} : {lines} lignes > 500"]
    if file.suffix == ".py":
        return check_python(path, text)
    return []


def audit(root, tree):
    paths = git_paths(["ls-tree", "-r", "--name-only", tree])
    missing = [p for p in DOC_TREE if not (root / p).is_file()]
    issues = [f"Documentation requise absente : {p}" for p in missing]
    for p in filter(is_code, paths):
        issues.extend(source_checks(root, p))
    go = [p for p in paths if p.endswith(".go")]
    if go:
        subprocess.run(["go", "run", "./quality/gocheck/main.go", "--", *go], cwd=root, check=True)
    if issues:
        raise ValueError("\n".join(issues))


def main(args):
    root, base, tree = args
    root = Path(root)
    audit(root, tree)
    message = root.parent / "message"
    tags = declarations(message.read_text()) if message.exists() else {}
    doc_policy(root, (base, tree), tags)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (ValueError, OSError, SyntaxError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Qualité : {error}")
