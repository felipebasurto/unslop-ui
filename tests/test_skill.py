import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "unslop-ui")
COUNTER = os.path.join(SKILL, "scripts", "count_tells.py")
LOADER = os.path.join(SKILL, "scripts", "load_unslop.py")


def run(script, *args, env=None):
    return subprocess.run(
        [sys.executable, script, *args], capture_output=True, text=True, env=env, cwd=ROOT
    )


def count(path):
    result = run(COUNTER, path)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class CounterTest(unittest.TestCase):
    def test_finds_planted_tells(self):
        counts = count(os.path.join(ROOT, "examples", "before"))
        expected = {
            "U1 eyebrow": 5,
            "U2 decorative numbering": 3,
            "U6 status string": 4,
            "U9 badge word": 3,
            "U10 status dot": 2,
            "U11 emoji": 6,
            "unslop 13 em dash": 3,
        }
        for rule, n in expected.items():
            self.assertEqual(counts[rule]["count"], n, rule)

    def test_cleaned_examples_are_clean(self):
        self.assertEqual(count(os.path.join(ROOT, "examples", "after"))["total"], 0)

    def test_ignores_code_comments(self):
        with tempfile.NamedTemporaryFile("w", suffix=".tsx", delete=False) as f:
            f.write("// 01 — a comment with an em dash 🚀\nconst x = 1;\n")
        try:
            self.assertEqual(count(f.name)["total"], 0)
        finally:
            os.unlink(f.name)

    def test_missing_path_fails(self):
        self.assertEqual(run(COUNTER, "does/not/exist").returncode, 2)


class LoaderTest(unittest.TestCase):
    def test_falls_back_without_pstack(self):
        with tempfile.TemporaryDirectory() as home:
            result = run(LOADER, env={**os.environ, "HOME": home})
        self.assertEqual(result.returncode, 0)
        self.assertIn("not installed", result.stdout)

    def test_picks_newest_pstack(self):
        with tempfile.TemporaryDirectory() as home:
            for version, marker in (("0.15.9", "OLD"), ("0.15.20", "NEW")):
                d = os.path.join(home, ".claude/plugins/cache/x/pstack", version, "skills/unslop")
                os.makedirs(d)
                with open(os.path.join(d, "SKILL.md"), "w") as f:
                    f.write("---\nname: unslop\n---\n# Unslop\n\n## Patterns to detect and fix\n" + marker + "\n")
            result = run(LOADER, env={**os.environ, "HOME": home})
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.startswith("## Patterns to detect and fix"))
        self.assertIn("NEW", result.stdout)


class FrontmatterTest(unittest.TestCase):
    def test_follows_agent_skills_spec(self):
        with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertTrue(text.startswith("---\n"))
        front = text.split("---\n")[1]
        name_match = re.search(r"^name:\s*(.+)$", front, re.M)
        description_match = re.search(r"^description:\s*\"(.+)\"$", front, re.M)
        assert name_match and description_match, front
        name = name_match.group(1).strip()
        description = description_match.group(1)
        self.assertEqual(name, os.path.basename(SKILL))
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertLessEqual(len(description), 1024)
        self.assertLess(text.count("\n"), 500)


if __name__ == "__main__":
    unittest.main()
