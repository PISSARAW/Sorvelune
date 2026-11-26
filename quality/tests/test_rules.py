import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "quality"))
from python_rules import check


class PolicyTests(unittest.TestCase):
    def test_parameters_depth_complexity_and_receivers(self):
        self.assertTrue(check("p.py", "def f(a, b, *, c, d): pass"))
        self.assertFalse(check("p.py", "class A:\n def f(self, a, b, c): pass"))
        self.assertTrue(check("p.py", "class A:\n @staticmethod\n def f(self, a, b, c): pass"))
        nested = "def f():\n" + "".join(" "*i + "if 1:\n" for i in range(1, 5)) + "     pass"
        self.assertTrue(check("p.py", nested))
        self.assertTrue(check("p.py", "def f(x):\n" + " if x: pass\n"*10))
        self.assertFalse(check("p.py", "def f(x):\n" + " if x: pass\n"*9))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for folder in ("quality", "docs", ".githooks"):
            shutil.copytree(ROOT / folder, self.root / folder, ignore=shutil.ignore_patterns("__pycache__", "gocheck"))
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "core.hooksPath", ".githooks")
        self.git("add", ".")
        self.commit("majeur", True)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True,
                              env={**os.environ, "GIT_CONFIG_NOSYSTEM": "1"})

    def commit(self, level, success):
        msg = f"Fixture de gouvernance\n\nImpact: {level}\nDesign-Review: KISS, SOLID"
        result = self.git("commit", "-qm", msg)
        self.assertEqual(result.returncode == 0, success, result.stderr)

    def test_unstaged_fix_does_not_hide_rejected_index(self):
        source = self.root / "app.py"
        source.write_text("def f(a,b,c,d): pass\n")
        (self.root / "README.md").write_text("Guide du scénario")
        self.git("add", ".")
        source.write_text("def f(a): pass\n")
        self.commit("important", False)
        self.git("add", "app.py")
        self.commit("important", True)

    def test_500_lines_and_documentation_are_blocking(self):
        source = self.root / "app.py"
        source.write_text("# ligne\n"*500)
        self.git("add", ".")
        self.commit("important", False)
        (self.root / "README.md").write_text("Guide du scénario")
        self.git("add", ".")
        self.commit("important", True)
        source.write_text("# ligne\n"*501)
        self.git("add", ".")
        result = self.git("commit", "-qm", "Trop long")
        self.assertIn("501 lignes", result.stderr)

    def test_major_requires_new_complete_adr_and_design_attestation(self):
        (self.root / "app.py").write_text("x = 1\n")
        (self.root / "README.md").write_text("Guide du scénario")
        self.git("add", ".")
        self.commit("majeur", False)
        adr = self.root / "docs/adr/0002-test.md"
        adr.write_text("## Décision\nUn choix.")
        self.git("add", ".")
        self.commit("majeur", False)
        adr.write_text((self.root / "docs/adr/0001-gouvernance.md").read_text())
        self.git("add", ".")
        result = self.git("commit", "-qm", "Fixture\n\nImpact: majeur")
        self.assertIn("Design-Review", result.stderr)
        self.commit("majeur", True)
