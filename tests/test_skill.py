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
PLUGIN = os.path.join(ROOT, "plugins", "unslop-ui")
PLUGIN_SKILL = os.path.join(PLUGIN, "skills", "unslop-ui")

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
            "unslop 7 AI vocabulary": 4,
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

    def test_counts_an_icon_in_a_tinted_tile(self):
        tile = '<span className="grid size-10 place-items-center rounded-lg bg-sky-100"><Icon className="size-4" /></span>\n'
        self.assertEqual(count_source(tile, ".tsx")["U11 icon tile"], 1)
        self.assertEqual(count_source('<div class="h-9 w-9 rounded-md bg-indigo-500/10"><svg></svg></div>\n', ".html")["U11 icon tile"], 1)

    def test_leaves_icon_buttons_avatars_and_tiles_with_text_alone(self):
        source = (
            '<button aria-label="Menu" className="size-10 rounded-lg"><MenuIcon /></button>\n'
            '<span className="size-10 rounded-full bg-sky-100"><img src="a.png" /></span>\n'
            '<span className="size-10 rounded-lg bg-sky-100">AB</span>\n'
            '<span className="rounded-lg bg-sky-100 px-2">NEW</span>\n'
        )
        self.assertEqual(count_source(source, ".tsx")["U11 icon tile"], 0)

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

    def test_taste_rules_run_only_when_the_taste_file_bans_them(self):
        source = '<h1>Welcome back!</h1>\n<Button className="uppercase">Save</Button>\n<span>Jan 3 \u00b7 14:02</span>\n'
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "page.tsx")
            taste = os.path.join(folder, "taste.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(source)
            plain = count(path)
            self.assertFalse([rule for rule in plain if rule.startswith("T")])
            self.assertEqual(plain["total"], 0)
            for ban, rule in [("Exclamation marks", "T1 exclamation mark"), ("All caps", "T2 uppercase text"), ("Middle dots between items", "T3 middle dot")]:
                with open(taste, "w", encoding="utf-8") as f:
                    f.write("# Taste\n\n## Bans\n\n- {}\n\n## Keep\n\n- Exclamation marks in the footer\n".format(ban))
                counts = count("--taste", taste, path)
                self.assertEqual(counts[rule], 1, rule)
                self.assertEqual(counts["total"], 1, rule)

    def test_taste_file_is_found_in_the_working_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            os.mkdir(os.path.join(folder, ".unslop-ui"))
            with open(os.path.join(folder, ".unslop-ui", "taste.md"), "w", encoding="utf-8") as f:
                f.write("## Bans\n\n- Exclamation marks\n")
            with open(os.path.join(folder, "a.html"), "w", encoding="utf-8") as f:
                f.write("<p>Saved!</p>\n")
            result = subprocess.run([sys.executable, COUNTER, "."], capture_output=True, text=True, cwd=folder)
        self.assertEqual(json.loads(result.stdout)["T1 exclamation mark"]["count"], 1)

    def test_a_missing_taste_file_fails_and_the_taste_folder_is_not_scanned(self):
        self.assertEqual(run(COUNTER, "--taste", "nope.md", os.path.join(ROOT, "examples")).returncode, 2)
        with tempfile.TemporaryDirectory() as folder:
            os.mkdir(os.path.join(folder, ".unslop-ui"))
            with open(os.path.join(folder, ".unslop-ui", "taste.md"), "w", encoding="utf-8") as f:
                f.write("## Bans\n\n- Exclamation marks\n\nNo more \u2014 and no emoji \U0001F680!\n")
            self.assertEqual(count(folder)["total"], 0)

    def test_counts_arrows_on_links_and_buttons(self):
        source = (
            '<a href="/x">Learn more →</a>\n'
            '<Link href="/x">Read the docs <span aria-hidden>→</span></Link>\n'
            '<Button>Get started <ArrowRight className="size-4" /></Button>\n'
            '<a href="/x">Learn more &rarr;</a>\n'
            'const cta = { label: "See pricing →" };\n'
        )
        self.assertEqual(count_source(source, ".tsx")["U21 arrow link"], 5)
        self.assertEqual(count_source("[Learn more →](/docs)\n", ".md")["U21 arrow link"], 1)
        prose = 'Mapping: humedades → "cubo"; fontanería → "llave". Then `01` → `02` → `03`.\n'
        self.assertEqual(count_source(prose, ".md")["U21 arrow link"], 0)

    def test_leaves_arrows_that_carry_meaning_alone(self):
        source = (
            '<button aria-label="Next">→</button>\n'
            '<Button onClick={() => next()}>→</Button>\n'
            '<button aria-label="Next"><ArrowRight /></button>\n'
            '<p>Step one → step two</p>\n'
            '<a href="https://x.dev">Docs ↗</a>\n'
            '<Link href="/a">Docs</Link> → <Link href="/b">API</Link>\n'
            '<Button variant="outline" size="icon"\n  {...props}\n>\n  <ArrowRight className="h-4 w-4" />\n  <span className="sr-only">Next</span>\n</Button>\n'
        )
        self.assertEqual(count_source(source, ".tsx")["U21 arrow link"], 0)

    def test_counts_generic_link_labels_only_on_links_and_buttons(self):
        source = (
            '<a href="/x">Click here</a>\n<button type="submit">Submit</button>\n'
            '<Link href="/docs">Learn more</Link>\n<a href="/es">Más información</a>\n'
        )
        self.assertEqual(count_source(source, ".tsx")["U23 vague link label"], 4)
        legit = '<h2>Here</h2>\n<span>Learn more</span>\n<a href="/p">Read the pricing guide</a>\n<button>Submit order</button>\n'
        self.assertEqual(count_source(legit, ".tsx")["U23 vague link label"], 0)

    def test_counts_filler_vocabulary_in_text_but_not_in_code(self):
        source = (
            '<p>Seamlessly manage a robust, cutting-edge workflow.</p>\n'
            'const hero = "Empower your team";\n'
            'const robustParse = () => seamlessScroll;\n'
            '<div className="seamless-grid robust-card" />\n'
            '// seamless\n'
        )
        self.assertEqual(count_source(source, ".tsx")["unslop 7 AI vocabulary"], 4)
        self.assertEqual(count_source("We leverage your data. Leverage is also a finance term.\n", ".md")["unslop 7 AI vocabulary"], 1)
        self.assertEqual(count_source('{"sub": "Gestiona tu dinero sin fisuras"}\n', ".json")["unslop 7 AI vocabulary"], 1)

    def test_counts_spanish_copy(self):
        source = (
            '<span>NUEVO</span>\n<span class="chip">Destacado</span>\n<button>Nuevo</button>\n'
            '<h2>Gráfico de barras de ingresos</h2>\n<p>Cada barra representa un mes. Pasa el cursor para ver el valor.</p>\n'
            '<p>Una solución integral de última generación.</p>\n'
        )
        counts = count_source(source, ".html")
        self.assertEqual(counts["U9 badge word"], 2)
        self.assertEqual(counts["U12 chart-type title"], 1)
        self.assertEqual(counts["U13 reading instructions"], 1)
        self.assertEqual(counts["unslop 7 AI vocabulary"], 2)

    def test_counts_edge_accent_bars_with_surface(self):
        source = (
            '<div className="rounded-lg border-l-4 border-indigo-500 p-4">a</div>\n'
            '<div className="border-s-[3px] border-primary">b</div>\n'
            '.card { border-left: 4px solid #6366f1; }\n'
        )
        self.assertEqual(count_source(source, ".tsx", "--surface")["U26 edge accent bar"], 3)
        self.assertNotIn("U26 edge accent bar", count_source(source, ".tsx"))
        legit = (
            '<div className="border-l-4 border-gray-200">a</div>\n<div className="border-l border-red-500">b</div>\n'
            '<div className="border-t-4 border-indigo-500">c</div>\n<div className="border-l-4">d</div>\n'
            '<div className="border-4 border-indigo-500">e</div>\n<div className="border-l-2 border-indigo-500">f</div>\n'
            '.quote { border-left: 2px solid var(--accent); }\n'
        )
        self.assertEqual(count_source(legit, ".tsx", "--surface")["U26 edge accent bar"], 0)

    def test_scroll_reveal_counts_as_motion(self):
        counts = count_source('<motion.div whileInView={{ opacity: 1 }} />\n<div data-aos="fade-up" />\n', ".tsx", "--surface")
        self.assertEqual(counts["U20 motion"], 2)

    def test_taste_off_switches_rules_off(self):
        source = '<h1>🚀 Fast — and simple</h1>\n<p className="uppercase tracking-widest">Eyebrow</p>\n'
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "page.tsx")
            taste = os.path.join(folder, "taste.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(source)
            with open(taste, "w", encoding="utf-8") as f:
                f.write("## Bans\n\n- Exclamation marks\n\n## Off\n\n- U11 we use emoji in product names\n- unslop 13, the brand writes with dashes\n")
            counts = count("--taste", taste, path)
            result = run(COUNTER, "--taste", taste, path)
        self.assertNotIn("U11 emoji", counts)
        self.assertNotIn("unslop 13 em dash", counts)
        self.assertEqual(counts["U1 eyebrow"], 1)
        self.assertIn("Off by taste file: U11, unslop 13", result.stderr)

    def test_github_format_prints_annotations_and_a_summary(self):
        result = run(COUNTER, "--format", "github", "--max", "0", os.path.join(ROOT, "examples", "before"))
        self.assertEqual(result.returncode, 1)
        lines = result.stdout.splitlines()
        self.assertTrue(lines[0].startswith("::warning file=examples/before/"), lines[0])
        self.assertRegex(lines[0], r",line=\d+,title=U1 eyebrow::")
        self.assertEqual(lines[-1], "unslop-ui: 35 possible tells")
        clean = run(COUNTER, "--format", "github", "--max", "0", os.path.join(ROOT, "examples", "after"))
        self.assertEqual((clean.returncode, clean.stdout.strip()), (0, "unslop-ui: 0 possible tells"))

    def test_agent_config_folders_are_not_scanned(self):
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, ".claude", "skills", "x"))
            with open(os.path.join(folder, ".claude", "skills", "x", "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("A — dash and 🚀 emoji\n")
            self.assertEqual(count(folder)["total"], 0)

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
        self.assertEqual(defined, {"U{}".format(n) for n in range(1, 27)})
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


class IncidentTest(unittest.TestCase):
    """Each incident is a reported false positive or miss, kept as a regression case."""

    def test_every_incident_still_holds(self):
        incidents = evals_run.load_incidents()
        self.assertGreaterEqual(len(incidents), 8)
        ids = [i["id"] for i in incidents]
        self.assertEqual(len(ids), len(set(ids)))
        for incident in incidents:
            self.assertEqual(evals_run.check_incident(incident), [], incident["id"])

    def test_every_incident_has_the_fields_and_a_matching_file_name(self):
        for name in os.listdir(evals_run.INCIDENTS):
            incident = json.loads(read_text(evals_run.INCIDENTS, name))
            self.assertEqual(name, incident["id"] + ".json")
            self.assertTrue(incident["report"])
            self.assertTrue(incident["rule"]["phrase"])
            self.assertTrue(incident["counter"]["source"])
            self.assertTrue(incident["counter"]["expect"])

    def test_an_incident_fails_when_the_rule_is_deleted_or_the_counter_regresses(self):
        incident = evals_run.load_incidents()[0]
        gone = {**incident, "rule": {**incident["rule"], "phrase": "a sentence nobody wrote"}}
        self.assertEqual(len(evals_run.check_incident(gone)), 1)
        wrong = {**incident, "counter": {**incident["counter"], "expect": {"U9 badge word": 5}}}
        self.assertIn("U9 badge word: expected 5, counted 0", evals_run.check_incident(wrong))


HOOK = os.path.join(SKILL, "scripts", "hook.py")
ACTION_SCRIPT = os.path.join(ROOT, "scripts", "action.sh")


def read_if_present(path):
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def run_hook(payload, env=None, cwd=ROOT):
    return subprocess.run(
        [sys.executable, HOOK], input=json.dumps(payload), capture_output=True, text=True, cwd=cwd,
        env={**os.environ, **(env or {})},
    )


class HookTest(unittest.TestCase):
    """The edit hook is opt-in and must never get in the agent's way."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = os.path.realpath(self.folder.name)

    def write(self, name, text):
        path = os.path.join(self.root, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_tells_a_claude_code_agent_what_it_just_wrote(self):
        path = self.write("hero.html", '<p class="uppercase tracking-widest">Introducing</p><h1>Hi</h1>\n')
        result = run_hook({"hook_event_name": "PostToolUse", "cwd": self.root, "tool_name": "Write", "tool_input": {"file_path": path}})
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PostToolUse")
        self.assertIn("unslop-ui found 1 possible AI tell in hero.html: U1 eyebrow x1 (line 1)", output["additionalContext"])

    def test_tells_a_cursor_agent_in_cursor_format(self):
        path = self.write("src/Hero.tsx", "export const A = () => <p>🚀 Launch</p>;\n")
        result = run_hook({"hook_event_name": "postToolUse", "cursor_version": "2026.10", "workspace_roots": [self.root], "tool_name": "Write", "tool_input": {"file_path": path}})
        text = json.loads(result.stdout)["additional_context"]
        self.assertIn("in src/Hero.tsx: U11 emoji x1 (line 1)", text)

    def test_stays_silent_on_a_clean_file_and_on_files_it_does_not_scan(self):
        clean = self.write("a.html", "<h1>Pricing</h1>\n")
        other = self.write("a.py_", "x")
        dep = self.write("node_modules/x/index.js", "<p>🚀</p>\n")
        for path in (clean, other, dep, os.path.join(self.root, "missing.html")):
            result = run_hook({"hook_event_name": "PostToolUse", "cwd": self.root, "tool_input": {"file_path": path}})
            self.assertEqual((result.returncode, result.stdout), (0, ""), path)

    def test_fails_open_on_bad_input(self):
        for raw in ("", "not json", "[]", '{"tool_input": null}'):
            result = subprocess.run([sys.executable, HOOK], input=raw, capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((result.returncode, result.stdout), (0, ""), raw)

    def test_honors_the_taste_file_and_the_surface_switch(self):
        path = self.write("a.html", '<h1>Welcome back!</h1>\n<p class="mt-[13px]">x</p>\n')
        payload = {"hook_event_name": "PostToolUse", "cwd": self.root, "tool_input": {"file_path": path}}
        self.assertEqual(run_hook(payload).stdout, "")
        self.write(".unslop-ui/taste.md", "## Bans\n\n- Exclamation marks\n")
        self.assertIn("T1 exclamation mark x1", run_hook(payload).stdout)
        self.write(".unslop-ui/taste.md", "## Bans\n\n- Exclamation marks\n\n## Off\n\n- T1, we like them\n")
        self.assertEqual(run_hook(payload).stdout, "")
        self.assertIn("U18 off-scale spacing x1", run_hook(payload, env={"UNSLOP_UI_SURFACE": "1"}).stdout)

    def test_example_configs_point_at_the_script_and_the_right_events(self):
        claude = json.loads(read_text(ROOT, "examples", "hooks", "claude-settings.json"))
        entry = claude["hooks"]["PostToolUse"][0]
        self.assertIn("Write", entry["matcher"])
        self.assertTrue(entry["hooks"][0]["command"].endswith("scripts/hook.py"))
        cursor = json.loads(read_text(ROOT, "examples", "hooks", "cursor-hooks.json"))
        self.assertEqual(cursor["version"], 1)
        self.assertEqual(cursor["hooks"]["postToolUse"][0]["matcher"], "Write")
        self.assertTrue(cursor["hooks"]["postToolUse"][0]["command"].endswith("scripts/hook.py"))


class ActionTest(unittest.TestCase):
    def run_action(self, **inputs):
        with tempfile.TemporaryDirectory() as folder:
            output, summary = os.path.join(folder, "output"), os.path.join(folder, "summary")
            env = {**os.environ, "GITHUB_OUTPUT": output, "GITHUB_STEP_SUMMARY": summary}
            env.update({"INPUT_" + key.upper(): value for key, value in inputs.items()})
            result = subprocess.run(["bash", ACTION_SCRIPT], capture_output=True, text=True, cwd=ROOT, env=env)
            return result, read_if_present(output), read_if_present(summary)

    def test_fails_above_the_limit_and_reports_the_total(self):
        result, output, summary = self.run_action(path="examples/before", max="0")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("::warning file=examples/before/"))
        self.assertEqual(output.strip(), "total=35")
        self.assertIn("35 possible tells (limit: 0)", summary)

    def test_passes_a_clean_folder_and_reports_without_a_limit(self):
        result, output, _ = self.run_action(path="examples/after", max="0", surface="true")
        self.assertEqual((result.returncode, output.strip()), (0, "total=0"))
        result, output, summary = self.run_action(path="examples/before examples/after")
        self.assertEqual((result.returncode, output.strip()), (0, "total=35"))
        self.assertIn("(limit: no limit)", summary)

    def test_a_missing_path_fails_without_a_total(self):
        result, output, _ = self.run_action(path="does/not/exist")
        self.assertEqual((result.returncode, output), (2, ""))

    def test_action_file_is_a_composite_action_that_runs_the_script(self):
        text = read_text(ROOT, "action.yml")
        self.assertIn("using: composite", text)
        self.assertIn('scripts/action.sh', text)
        for name in ("path", "max", "surface", "taste"):
            self.assertRegex(text, r"(?m)^  %s:$" % name)
            self.assertIn("INPUT_%s: ${{ inputs.%s }}" % (name.upper(), name), text)
        self.assertIn("value: ${{ steps.count.outputs.total }}", text)


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
ALLOWED_PLUGIN_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml"} | IMAGE_SUFFIXES


def read_text(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


def between(text, start, end):
    return text[text.index(start):text.index(end)]


class PluginTest(unittest.TestCase):
    """The Claude plugin directory refuses scripts, inline shell and broad allowed-tools."""

    def plugin_files(self):
        for folder, _, names in os.walk(PLUGIN):
            for name in names:
                yield os.path.join(folder, name)

    def test_ships_only_text_and_images(self):
        for path in self.plugin_files():
            suffix = os.path.splitext(path)[1].lower()
            if os.path.basename(path) == "LICENSE":
                continue
            self.assertIn(suffix, ALLOWED_PLUGIN_SUFFIXES, path)
            with open(path, "rb") as f:
                data = f.read()
            self.assertFalse(data.startswith(b"#!"), path)
            if suffix not in IMAGE_SUFFIXES:
                self.assertNotIn(b"\x00", data, path)

    def test_skill_has_no_inline_shell_and_minimal_tools(self):
        text = read_text(PLUGIN_SKILL, "SKILL.md")
        self.assertNotIn("!`", text)
        self.assertNotIn("```!", text)
        self.assertNotIn("${", text)
        self.assertIn("allowed-tools: Read, Grep, Glob, LS\n", text)

    def test_manifest_and_marketplace_agree(self):
        manifest = json.loads(read_text(PLUGIN, ".claude-plugin", "plugin.json"))
        marketplace = json.loads(read_text(ROOT, ".claude-plugin", "marketplace.json"))
        self.assertEqual(manifest["name"], "unslop-ui")
        self.assertEqual(marketplace["plugins"][0]["source"], "./plugins/unslop-ui")
        self.assertTrue(os.path.isdir(os.path.join(ROOT, marketplace["plugins"][0]["source"])))

    def test_rules_match_the_skill_build(self):
        for start, end in [("## UI rules", "## Guardrails"), ("## Cut first", "## UI rules"), ("## Guardrails", "## Procedure")]:
            self.assertEqual(
                between(read_text(SKILL, "SKILL.md"), start, end),
                between(read_text(PLUGIN_SKILL, "SKILL.md"), start, end),
                start,
            )
        for name in ("examples.md", "tokens.md", "unslop-fallback.md", "taste-example.md"):
            self.assertEqual(read_text(SKILL, "references", name), read_text(PLUGIN_SKILL, "references", name), name)

    def test_links_exist(self):
        text = read_text(PLUGIN_SKILL, "SKILL.md")
        for target in re.findall(r"\]\((references/[^)]+)\)", text):
            self.assertTrue(os.path.exists(os.path.join(PLUGIN_SKILL, target)), target)

    def test_every_counted_rule_has_a_search_pattern(self):
        patterns = read_text(PLUGIN_SKILL, "references", "finding-tells.md")
        for rule in ["U1", "U2", "U6", "U9", "U10", "U11", "U12", "U13", "U15", "U16", "U17", "U18", "U19", "U20", "U21", "U23", "U26", "T1", "T2", "T3", "unslop 7", "unslop 13"]:
            self.assertIn("**" + rule + " ", patterns)


if __name__ == "__main__":
    unittest.main()
