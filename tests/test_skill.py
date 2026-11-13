import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "unslop-ui")
COUNTER = os.path.join(SKILL, "scripts", "count_tells.py")
LOADER = os.path.join(SKILL, "scripts", "load_unslop.py")

_spec = importlib.util.spec_from_file_location("evals_run", os.path.join(ROOT, "evals", "run.py"))
evals_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(evals_run)


def run(script, *args, env=None):
    return subprocess.run(
        [sys.executable, script, *args], capture_output=True, text=True, env=env, cwd=ROOT
    )


def count(*args):
    result = run(COUNTER, *args)
    assert result.returncode == 0, result.stderr
    return {rule: (entry if rule == "total" else entry["count"]) for rule, entry in json.loads(result.stdout).items()}


def count_source(source, suffix, *flags):
    """Counts for a source string written to a temporary file with this suffix."""
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "sample" + suffix)
        with open(path, "w", encoding="utf-8") as f:
            f.write(source)
        return count(*flags, path)


class CounterTest(unittest.TestCase):
    def test_finds_planted_tells(self):
        counts = count(os.path.join(ROOT, "examples", "before"))
        expected = {
            "U1 eyebrow": 5,
            "U2 decorative numbering": 3,
            "U6 status string": 2,
            "U9 badge word": 3,
            "U10 status dot": 2,
            "U11 emoji": 6,
            "U12 chart-type title": 1,
            "U13 reading instructions": 1,
            "U15 chart scaffolding": 4,
            "U16 legend": 1,
            "unslop 13 em dash": 3,
        }
        for rule, n in expected.items():
            self.assertEqual(counts[rule], n, rule)
        self.assertEqual(counts["total"], sum(expected.values()))

    def test_cleaned_examples_are_clean(self):
        self.assertEqual(count("--surface", os.path.join(ROOT, "examples", "after"))["total"], 0)

    def test_ignores_code_comments(self):
        source = (
            "// 01 — a comment with an em dash 🚀\n"
            "const x = 1; // 02 — trailing 🚀\n"
            "/* block — 🚀\n   second line — 🚀 */\n"
            "const view = <div>{/* note — 🚀 */}<!-- old — 🚀 --></div>;\n"
        )
        self.assertEqual(count_source(source, ".tsx")["total"], 0)

    def test_keeps_text_that_looks_like_a_comment(self):
        counts = count_source('<span>01 // Features</span>\n<a href="https://example.com">x</a>\n', ".html")
        self.assertEqual(counts["U2 decorative numbering"], 1)

    def test_leaves_legitimate_patterns_alone(self):
        source = """
export function Legit({ rows, loading, progress }) {
  return (
    <div>
      {loading && <div className="h-4 w-32 animate-pulse rounded bg-muted" />}
      <Skeleton className="h-4 w-32 animate-pulse" />
      <div className="h-2 w-full overflow-hidden rounded-full bg-secondary" />
      <img className="h-10 w-10 rounded-full" />
      <Button>New</Button>
      <td>Pro</td>
      <th className="text-xs uppercase tracking-wide">Amount</th>
      <h1 className="uppercase tracking-tight">Sale</h1>
      <td>{row.amount ?? "—"}</td>
      <td>—</td>
      <button aria-label="Close">✕</button>
      <li>✓ Unlimited seats</li>
      <option value="01">January</option>
      <time>01/02/2026 01:30</time>
      <span>Jan 3 · 14:02</span>
      <input className="px-3 py-[10px]" />
    </div>
  );
}
"""
        self.assertEqual(count_source(source, ".tsx", "--surface")["total"], 0)

    def test_counts_a_status_dot_in_any_class_order(self):
        source = (
            '<span className="h-2 w-2 rounded-full bg-green-500" />\n'
            '<span className="rounded-full bg-green-500 size-1.5" />\n'
            '<span className="text-green-500 animate-pulse">Live</span>\n'
        )
        self.assertEqual(count_source(source, ".tsx")["U10 status dot"], 3)

    def test_counts_generated_numbering(self):
        source = '<span>{String(i + 1).padStart(2, "0")}</span>\n<span>\n  02\n</span>\n<b>0{i + 1}</b>\n'
        self.assertEqual(count_source(source, ".tsx")["U2 decorative numbering"], 3)

    def test_counts_an_eyebrow_split_over_lines(self):
        source = '<p\n  className="text-xs font-medium uppercase\n    tracking-widest text-indigo-500"\n>\n  Features\n</p>\n'
        self.assertEqual(count_source(source, ".tsx")["U1 eyebrow"], 1)

    def test_counts_badges_by_shape(self):
        source = "<Badge>Most popular</Badge>\n<span>Beta</span>\n<div>NEW</div>\n<Button>New</Button>\n"
        self.assertEqual(count_source(source, ".tsx")["U9 badge word"], 3)

    def test_counts_a_chain_once_and_skips_a_single_separator(self):
        source = (
            "<p>12 items · Updated 2m ago · Synced · v2.1</p>\n"
            + "<p>filler</p>\n" * 20
            + "<p>Jan 3 · 14:02</p>\n"
            + "<p>filler</p>\n" * 20
            + "<p>Docs | Blog | Careers</p>\n<p>{facts.join(' · ')}</p>\n"
        )
        self.assertEqual(count_source(source, ".tsx")["U6 status string"], 3)

    def test_counts_a_chart_config_formatted_over_lines(self):
        source = """
export const options = {
  plugins: {
    legend: {
      display: true,
      position: "bottom",
    },
  },
  scales: {
    y: {
      grid: {
        color: "#9ca3af",
        lineWidth: 2,
      },
      border: {
        display: true,
        width: 2,
      },
    },
  },
};
"""
        counts = count_source(source, ".js")
        self.assertEqual(counts["U15 chart scaffolding"], 2)
        self.assertEqual(counts["U16 legend"], 1)

    def test_allows_hairline_chart_baseline(self):
        source = 'x: { grid: { lineWidth: 1 }, border: { display: true, width: 1 } },\n'
        self.assertEqual(count_source(source, ".js")["total"], 0)

    def test_counts_python_charts(self):
        source = (
            "# 🚀 a comment — ignored\n"
            'ax.set_title("📈 Bar chart of monthly revenue")\n'
            "ax.grid(True, linewidth=2)\n"
            "ax.legend()\n"
        )
        counts = count_source(source, ".py")
        self.assertEqual(counts["U11 emoji"], 1)
        self.assertEqual(counts["U12 chart-type title"], 1)
        self.assertEqual(counts["U15 chart scaffolding"], 1)
        self.assertEqual(counts["U16 legend"], 1)
        self.assertEqual(counts["total"], 4)

    def test_counts_markdown_headings_and_lists(self):
        counts = count_source("# 🚀 Welcome — to the app\n* ✨ Feature one\n", ".md")
        self.assertEqual(counts["U11 emoji"], 2)
        self.assertEqual(counts["unslop 13 em dash"], 1)

    def test_scans_stylesheets_and_translations_in_a_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            with open(os.path.join(folder, "app.css"), "w", encoding="utf-8") as f:
                f.write(".eyebrow { text-transform: uppercase; }\n.card { padding: 11px; font-weight: 900; }\n")
            with open(os.path.join(folder, "en.json"), "w", encoding="utf-8") as f:
                f.write('{"cta": "🚀 Upgrade", "sub": "Fast — and simple"}\n')
            counts = count("--surface", folder)
        self.assertEqual(counts["U1 eyebrow"], 1)
        self.assertEqual(counts["U11 emoji"], 1)
        self.assertEqual(counts["unslop 13 em dash"], 1)
        self.assertEqual(counts["U18 off-scale spacing"], 1)
        self.assertEqual(counts["U19 extra-heavy weight"], 1)

    def test_surface_rules_are_opt_in(self):
        source = (
            '<div className="mt-[13px] p-[16px] gap-[7px] bg-gradient-to-r from-purple-500 to-blue-500 '
            'font-black transition-all hover:scale-105 shadow-[0_0_20px_rgba(0,0,0,.5)]">\n'
            "<h1 style={{ fontWeight: 800 }}>x</h1>\n"
            ".a { padding: 11px; margin: 8px 4px; transition: all .3s; }\n"
        )
        self.assertEqual(count_source(source, ".tsx")["total"], 0)
        counts = count_source(source, ".tsx", "--surface")
        self.assertEqual(counts["U17 gradient or glow"], 2)
        self.assertEqual(counts["U18 off-scale spacing"], 3)
        self.assertEqual(counts["U19 extra-heavy weight"], 2)
        self.assertEqual(counts["U20 motion"], 3)

    def test_surface_ignores_on_scale_spacing(self):
        source = '<div className="mt-[12px] p-[2px] py-[10px] gap-[24px] transition-colors">x</div>\n'
        self.assertEqual(count_source(source, ".tsx", "--surface")["total"], 0)

    def test_surface_counts_large_values_off_the_4px_grid(self):
        self.assertEqual(count_source('<div className="mt-[18px] p-[30px]" />\n', ".tsx", "--surface")["U18 off-scale spacing"], 2)

    def test_max_sets_the_exit_code(self):
        before = os.path.join(ROOT, "examples", "before")
        self.assertEqual(run(COUNTER, "--max", "0", before).returncode, 1)
        self.assertEqual(run(COUNTER, "--max", "1000", before).returncode, 0)

    def test_missing_path_fails(self):
        self.assertEqual(run(COUNTER, "does/not/exist").returncode, 2)


def install_unslop(home, folder, body):
    path = os.path.join(home, folder, "skills", "unslop")
    os.makedirs(path)
    with open(os.path.join(path, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write("---\nname: unslop\n---\n# Unslop\n\n" + body)


def load(home):
    result = run(LOADER, env={**os.environ, "HOME": home})
    assert result.returncode == 0, result.stderr
    return result.stdout


RULES = (
    "## Patterns to detect and fix\n\nRule numbers are stable.\n\n"
    "### Style\n\n13. **Em dash overuse.** {marker}\n19. **Curly quotes.** Use straight quotes.\n\n"
    "### Plain speech\n\n33. **Over-compression.** Write whole sentences.\n34. **A later rule.** Kept.\n\n"
    "## Process\n\nDraft, audit, rewrite.\n"
)


class LoaderTest(unittest.TestCase):
    def test_falls_back_to_bundled_rules_without_pstack(self):
        with tempfile.TemporaryDirectory() as home:
            output = load(home)
        self.assertIn("not installed", output)
        self.assertRegex(output, r"(?m)^13\. \*\*Em dashes")
        self.assertNotRegex(output, r"(?m)^33\. ")

    def test_keeps_only_the_rules_that_apply_to_interfaces(self):
        with tempfile.TemporaryDirectory() as home:
            install_unslop(home, ".claude/plugins/cache/x/pstack/1.0.0", RULES.format(marker="M"))
            output = load(home)
        self.assertTrue(output.startswith("### Style"), output)
        self.assertRegex(output, r"(?m)^13\. ")
        self.assertRegex(output, r"(?m)^34\. ")
        self.assertNotRegex(output, r"(?m)^(19|33)\. ")
        self.assertNotIn("Process", output)

    def test_picks_newest_version(self):
        with tempfile.TemporaryDirectory() as home:
            for version, marker in (("0.15.20", "NEW"), ("0.15.9", "OLD")):
                install_unslop(home, ".claude/plugins/cache/x/pstack/" + version, RULES.format(marker=marker))
            output = load(home)
        self.assertIn("NEW", output)
        self.assertNotIn("OLD", output)

    def test_picks_last_written_among_commit_hash_folders(self):
        with tempfile.TemporaryDirectory() as home:
            now = time.time()
            for commit, marker, age in (("9f00aaaa", "OLD", 3600), ("05b49176", "NEW", 0)):
                folder = ".cursor/plugins/cache/cursor-public/pstack/" + commit
                install_unslop(home, folder, RULES.format(marker=marker))
                written = now - age
                os.utime(os.path.join(home, folder, "skills", "unslop", "SKILL.md"), (written, written))
            output = load(home)
        self.assertIn("NEW", output)
        self.assertNotIn("OLD", output)

    def test_prints_an_unslop_with_an_unknown_layout_whole(self):
        with tempfile.TemporaryDirectory() as home:
            install_unslop(home, ".agents", "Write plainly. No em dashes.\n")
            output = load(home)
        self.assertIn("Write plainly", output)
        self.assertNotIn("name: unslop", output)


class SkillFileTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
            self.text = f.read()

    def test_follows_agent_skills_spec(self):
        self.assertTrue(self.text.startswith("---\n"))
        front = self.text.split("---\n")[1]
        name_match = re.search(r"^name:\s*(.+)$", front, re.M)
        description_match = re.search(r"^description:\s*\"(.+)\"$", front, re.M)
        assert name_match and description_match, front
        name = name_match.group(1).strip()
        self.assertEqual(name, os.path.basename(SKILL))
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertLessEqual(len(description_match.group(1)), 1024)
        self.assertLess(self.text.count("\n"), 500)

    def test_links_and_scripts_exist(self):
        targets = re.findall(r"\]\(([^)#]+)\)", self.text) + re.findall(r"scripts/\w+\.py", self.text)
        self.assertGreater(len(targets), 3)
        for target in targets:
            self.assertTrue(os.path.exists(os.path.join(SKILL, target)), target)

    def test_defines_every_rule_the_counter_reports(self):
        defined = set(re.findall(r"\*\*(U\d+)\. ", self.text))
        self.assertEqual(defined, {"U{}".format(n) for n in range(1, 21)})
        reported = {rule.split()[0] for rule in count("--surface", os.path.join(ROOT, "examples", "after")) if rule.startswith("U")}
        self.assertLessEqual(reported, defined)


class EvalFixturesTest(unittest.TestCase):
    """The agent run is manual (evals/run.py); these keep its checks honest."""

    def setUp(self):
        self.expectations = evals_run.load_expectations()

    def files(self):
        for name, fixture in self.expectations.items():
            for filename, spec in fixture["files"].items():
                yield name, filename, spec, evals_run.read(os.path.join(evals_run.FIXTURES, name, filename))

    def test_every_expectation_refers_to_text_in_its_fixture(self):
        for name, filename, spec, before in self.files():
            for needle in spec.get("keep", []) + spec.get("cut", []):
                self.assertIn(needle, before, "{}/{}".format(name, filename))
            for pattern in spec.get("keep_regex", []):
                self.assertRegex(before, pattern, "{}/{}".format(name, filename))

    def test_an_untouched_fixture_fails_unless_it_is_the_clean_one(self):
        for name, fixture in self.expectations.items():
            failed = evals_run.check_fixture(name, os.path.join(evals_run.FIXTURES, name), self.expectations)
            clean = all(spec.get("unchanged") for spec in fixture["files"].values())
            self.assertEqual(failed == {}, clean, name)

    def test_cutting_exactly_what_is_listed_passes(self):
        for name, filename, spec, before in self.files():
            after = before
            for needle in spec.get("cut", []):
                after = after.replace(needle, "")
            self.assertEqual(evals_run.check_file(before, after, spec), [], "{}/{}".format(name, filename))

    def test_reports_lost_text_invented_numbers_and_edits_to_a_clean_file(self):
        self.assertEqual(evals_run.check_file("a 12", "a 12 b", {"unchanged": True}), ["changed, expected no edit"])
        failures = evals_run.check_file("keep cut 12", "cut 12 in 3 seconds", {"keep": ["keep"], "cut": ["cut"], "no_new_numbers": True})
        self.assertEqual(failures, ["lost 'keep'", "still has 'cut'", "new numbers 3"])


if __name__ == "__main__":
    unittest.main()
