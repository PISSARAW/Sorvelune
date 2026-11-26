"""Mesures structurelles du Python, sur l'arbre syntaxique du fichier."""
import ast
from typing import NamedTuple


class Score(NamedTuple):
    branches: int
    depth: int


FUNCTION = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
CONTROL = (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.Try,
           ast.With, ast.AsyncWith, ast.Match)
DECISION = (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.comprehension)
COMPREHENSION = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def weight(node):
    if isinstance(node, ast.BoolOp):
        return len(node.values) - 1
    if isinstance(node, ast.comprehension):
        return 1 + len(node.ifs)
    if isinstance(node, ast.match_case):
        return int(node.guard is not None or not isinstance(node.pattern, ast.MatchAs) or node.pattern.pattern is not None)
    return int(isinstance(node, DECISION))


def child_levels(node, level):
    for child in ast.iter_child_nodes(node):
        # L'AST encode elif comme un if imbriqué sur la même colonne.
        alternate = isinstance(node, ast.If) and isinstance(child, ast.If) and child.col_offset == node.col_offset
        yield child, level - int(alternate)


def measure(node, level=0):
    if isinstance(node, (*FUNCTION, ast.ClassDef)):
        return Score(0, level)
    level += int(isinstance(node, CONTROL) or type(node).__name__ == "TryStar")
    if isinstance(node, COMPREHENSION):
        level += len(node.generators)
    children = [measure(child, depth) for child, depth in child_levels(node, level)]
    return Score(weight(node) + sum(c.branches for c in children),
                 max([level] + [c.depth for c in children]))


def parameters(fn, is_method):
    args = fn.args
    positional = args.posonlyargs + args.args
    receiver = bool(is_method and positional and positional[0].arg in {"self", "cls"})
    return len(positional) + len(args.kwonlyargs) + bool(args.vararg) + bool(args.kwarg) - receiver


def is_instance_method(fn):
    return isinstance(fn, FUNCTION) and not any(
        isinstance(d, ast.Name) and d.id == "staticmethod" for d in getattr(fn, "decorator_list", []))


def metrics(fn, is_method):
    body = [fn.body] if isinstance(fn, ast.Lambda) else fn.body
    scores = [measure(stmt) for stmt in body]
    return (("paramètres", parameters(fn, is_method), 3),
            ("profondeur", max((s.depth for s in scores), default=0), 3),
            ("complexité", 1 + sum(s.branches for s in scores), 10))


def functions(tree):
    return (node for node in ast.walk(tree) if isinstance(node, FUNCTION))


def scope_depth(path, tree):
    issues = []
    scopes = [tree, *(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))]
    for scope in scopes:
        depth = max((measure(stmt).depth for stmt in scope.body), default=0)
        if depth > 3:
            issues.append(f"{path}:{getattr(scope, 'lineno', 1)} profondeur {depth} > 3")
    return issues


def check(path, text):
    tree = ast.parse(text, filename=path)
    methods = set()
    for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
        methods.update(fn for fn in cls.body if is_instance_method(fn))
    issues = scope_depth(path, tree)
    for fn in functions(tree):
        for label, value, limit in metrics(fn, fn in methods):
            if value > limit:
                issues.append(f"{path}:{fn.lineno} {getattr(fn, 'name', 'lambda')} {label} {value} > {limit}")
    return issues
