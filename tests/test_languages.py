"""Tests for scripts/languages.py (run: python3 -m unittest discover -s tests -v).

No network: urllib.request.urlopen is replaced by a fake GitHub API.
"""
import importlib.util
import io
import json
import os
import re
import tempfile
import unittest
import urllib.error
import xml.etree.ElementTree as ET
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "scripts" / "languages.py"
spec = importlib.util.spec_from_file_location("languages", SRC)
lang = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lang)


class Resp(io.BytesIO):
    """What urlopen returns: json.load only needs read()."""
    def __enter__(self): return self
    def __exit__(self, *a): return False


def node(name, **langs):
    return {"nameWithOwner": f"me/{name}",
            "languages": {"edges": [{"size": s, "node": {"name": n, "color": None if n == "Nocolor" else "#123456"}}
                                    for n, s in langs.items()]}}


def page(nodes, nxt=None):
    return {"data": {"viewer": {"repositories": {
        "pageInfo": {"hasNextPage": nxt is not None, "endCursor": nxt}, "nodes": nodes}}}}


def tree(*files):
    return {"tree": [{"type": t, "path": p, "size": s} for p, s, t in files]}


class FakeGitHub:
    """Routes graphql pages and per-repo git trees; a repo mapped to an int answers with that HTTP error."""
    def __init__(self, pages, trees=None, tree_error=None):
        self.pages, self.trees, self.tree_error, self.calls = list(pages), trees or {}, tree_error, []

    def __call__(self, req):
        url = req.full_url
        self.calls.append(url)
        if url.endswith("/graphql"):
            return Resp(json.dumps(self.pages.pop(0)).encode())
        if self.tree_error:
            raise urllib.error.HTTPError(url, self.tree_error, "err", {}, None)
        repo = re.search(r"/repos/(.+?)/git/trees/", url).group(1)
        return Resp(json.dumps(self.trees.get(repo, {"tree": []})).encode())


def run_fetch(gh):
    with mock.patch.object(lang.urllib.request, "urlopen", gh), redirect_stderr(io.StringIO()):
        return lang.fetch("tok")


class MarkdownBytes(unittest.TestCase):
    def call(self, gh):
        err = io.StringIO()
        with mock.patch.object(lang.urllib.request, "urlopen", gh), redirect_stderr(err):
            return lang.markdown_bytes("tok", "me/r", "HEAD"), err.getvalue()

    def test_counts_only_md_blobs_case_insensitive(self):
        t = tree(("README.md", 100, "blob"), ("docs/A.MD", 50, "blob"), ("n.markdown", 7, "blob"),
                 ("docs", 0, "tree"), ("x.md.txt", 999, "blob"), ("app.py", 500, "blob"), ("notes.mdx", 40, "blob"))
        n, _ = self.call(FakeGitHub([], {"me/r": t}))
        self.assertEqual(n, 157)

    def test_empty_repo_is_zero(self):
        self.assertEqual(self.call(FakeGitHub([]))[0], 0)

    def test_forbidden_token_adds_zero_and_never_raises(self):
        """Regression: the metadata-only token got 403 and the whole card failed (run of 2026-11-28)."""
        for code in (403, 404, 409, 500):
            n, err = self.call(FakeGitHub([], tree_error=code))
            self.assertEqual(n, 0)
            self.assertIn("skipped", err)
            self.assertNotIn("me/r", err)  # never print repo names

    def test_requests_default_branch_tree_with_token(self):
        gh = FakeGitHub([])
        seen = []
        def spy(req):
            seen.append((req.full_url, req.get_header("Authorization")))
            return gh(req)
        with mock.patch.object(lang.urllib.request, "urlopen", spy):
            lang.markdown_bytes("sekret", "me/r", "HEAD")
        self.assertEqual(seen, [("https://api.github.com/repos/me/r/git/trees/HEAD?recursive=1", "bearer sekret")])


class Fetch(unittest.TestCase):
    def test_sums_languages_and_markdown_across_repos(self):
        gh = FakeGitHub([page([node("a", Python=100, HTML=40), node("b", Python=50, TeX=10)])],
                        {"me/a": tree(("a.md", 30, "blob")), "me/b": tree(("b.md", 20, "blob"))})
        totals, colors, repos = run_fetch(gh)
        self.assertEqual(repos, 2)
        self.assertEqual(totals, {"Python": 150, "TeX": 10, "Markdown": 50})  # HTML is skipped
        self.assertEqual(colors["Markdown"], "#083fa1")

    def test_tex_and_markdown_count_but_html_styles_and_build_files_do_not(self):
        self.assertTrue({"TeX", "Python"}.isdisjoint(lang.SKIP))
        self.assertNotIn("Markdown", lang.SKIP)
        self.assertLessEqual({"HTML", "CSS", "SCSS", "Makefile", "Dockerfile"}, lang.SKIP)
        gh = FakeGitHub([page([node("a", HTML=9, CSS=9, SCSS=9, Makefile=9, Dockerfile=9, TeX=1, Python=2)])])
        totals, _, _ = run_fetch(gh)
        self.assertEqual(totals, {"TeX": 1, "Python": 2})

    def test_missing_color_falls_back_to_grey(self):
        _, colors, _ = run_fetch(FakeGitHub([page([node("a", Nocolor=5)])]))
        self.assertEqual(colors["Nocolor"], "#8b949e")

    def test_follows_pagination(self):
        gh = FakeGitHub([page([node("a", Python=1)], nxt="C1"), page([node("b", Python=2)])])
        totals, _, repos = run_fetch(gh)
        self.assertEqual((totals["Python"], repos), (3, 2))

    def test_graphql_error_aborts_with_message(self):
        gh = FakeGitHub([{"errors": [{"type": "FORBIDDEN"}]}])
        with mock.patch.object(lang.urllib.request, "urlopen", gh):
            with self.assertRaises(SystemExit) as cm:
                lang.fetch("tok")
        self.assertIn("GraphQL error", str(cm.exception))

    def test_graphql_query_needs_only_metadata_fields(self):
        """Regression: defaultBranchRef needs Contents: read and was FORBIDDEN for the metadata-only token."""
        self.assertNotIn("defaultBranchRef", lang.QUERY)
        self.assertIn("isFork:false", lang.QUERY.replace(" ", ""))

    def test_forbidden_trees_still_give_a_card_without_markdown(self):
        gh = FakeGitHub([page([node("a", Python=10)])], tree_error=403)
        totals, _, _ = run_fetch(gh)
        self.assertEqual(totals, {"Python": 10})


ROWS = [(f"Lang{i}", 100 / 10, "#abcdef") for i in range(10)]


class Svg(unittest.TestCase):
    def test_shape_constants(self):
        self.assertEqual(lang.TOP, sum(lang.PYRAMID))
        self.assertEqual(lang.PYRAMID, sorted(lang.PYRAMID))  # grows downward: a pyramid

    def test_is_wellformed_xml_for_both_themes(self):
        for dark in (True, False):
            root = ET.fromstring(lang.svg(ROWS, dark))
            self.assertTrue(root.tag.endswith("svg"))

    def test_themes_differ(self):
        self.assertNotEqual(lang.svg(ROWS, True), lang.svg(ROWS, False))

    def test_all_ten_labels_with_percent(self):
        s = lang.svg(ROWS, False)
        for i in range(10):
            self.assertIn(f"Lang{i} ", s)
        self.assertEqual(s.count("10.0%"), 10)

    def test_pyramid_rows_are_1_2_3_4_and_symmetrical(self):
        root = ET.fromstring(lang.svg(ROWS, False))
        ns = "{http://www.w3.org/2000/svg}"
        w = float(root.get("width"))
        dots = [(float(c.get("cx")), float(c.get("cy"))) for c in root.iter(ns + "circle")]
        rows = {}
        for cx, cy in dots:
            rows.setdefault(cy, []).append(cx)
        self.assertEqual([len(v) for _, v in sorted(rows.items())], [1, 2, 3, 4])
        centers = [sum(v) / len(v) for _, v in sorted(rows.items())]
        for c in centers:
            self.assertAlmostEqual(c, centers[0], places=3)  # every row centred on the same axis
        self.assertTrue(all(0 <= cx <= w for cx, _ in dots))

    def test_bar_segments_fill_the_bar_and_stay_inside(self):
        root = ET.fromstring(lang.svg(ROWS, False))
        ns = "{http://www.w3.org/2000/svg}"
        segs = [r for r in root.iter(ns + "rect") if r.get("y") == "18" and r.get("fill") == "#abcdef"]
        self.assertEqual(len(segs), 10)
        self.assertAlmostEqual(float(segs[-1].get("x")) + float(segs[-1].get("width")), 20 + 420 + 0.5, delta=1)

    def test_names_are_escaped(self):
        s = lang.svg([("A&B <x>", 100.0, "#fff")], True)
        ET.fromstring(s)
        self.assertIn("A&amp;B &lt;x&gt;", s)

    def test_fewer_than_ten_languages_still_renders(self):
        s = lang.svg(ROWS[:4], False)
        ET.fromstring(s)
        self.assertEqual(s.count("<circle"), 4)

    def test_neighbouring_labels_keep_the_slot_spacing(self):
        """Rendered check (2026-11-28): 110 px slots keep 'TypeScript 1.5%' clear of the next dot."""
        root = ET.fromstring(lang.svg(ROWS, False))
        ns = "{http://www.w3.org/2000/svg}"
        bottom = sorted(float(c.get("cx")) for c in root.iter(ns + "circle") if float(c.get("cy")) == max(
            float(d.get("cy")) for d in root.iter(ns + "circle")))
        gaps = [b - a for a, b in zip(bottom, bottom[1:])]
        self.assertTrue(all(abs(g - 110) < 0.01 for g in gaps), gaps)


class MainIntegration(unittest.TestCase):
    def run_main(self, gh, env=None):
        out = tempfile.mkdtemp()
        out_buf, err_buf = io.StringIO(), io.StringIO()
        with mock.patch.object(lang.urllib.request, "urlopen", gh), \
                mock.patch.dict(os.environ, {"GH_TOKEN": "tok", **(env or {})}), \
                mock.patch("sys.argv", ["languages.py", out]), \
                redirect_stdout(out_buf), redirect_stderr(err_buf):
            lang.main()
        return out, out_buf.getvalue()

    def many(self):
        langs = {f"L{i:02d}": 1000 - i * 10 for i in range(14)}
        return FakeGitHub([page([node("a", **langs)])], {"me/a": tree(("d.md", 2000, "blob"))})

    def test_writes_light_and_dark_svg_with_top_ten_ranked(self):
        out, stdout = self.run_main(self.many())
        self.assertEqual(sorted(os.listdir(out)), ["languages-dark.svg", "languages.svg"])
        svg = Path(out, "languages.svg").read_text()
        ET.fromstring(svg)
        names = re.findall(r"<text[^>]*>([^<]+?) <tspan", svg)
        self.assertEqual(names, ["Markdown", "L00", "L01", "L02", "L03", "L04", "L05", "L06", "L07", "L08"])
        self.assertIn("top 10:", stdout)
        pcts = [float(p) for p in re.findall(r"<tspan[^>]*>([\d.]+)%", svg)]
        self.assertAlmostEqual(sum(pcts), 100.0, delta=0.5)
        self.assertEqual(pcts, sorted(pcts, reverse=True))

    def test_published_files_name_no_repository(self):
        out, stdout = self.run_main(self.many())
        for f in os.listdir(out):
            self.assertNotIn("me/a", Path(out, f).read_text())
        self.assertNotIn("me/a", stdout)

    def test_token_without_contents_permission_still_publishes_card_without_markdown(self):
        """End-to-end regression for the failed profile-art run."""
        langs = {f"L{i:02d}": 1000 - i * 10 for i in range(12)}
        gh = FakeGitHub([page([node("a", **langs)])], tree_error=403)
        out, _ = self.run_main(gh)
        svg = Path(out, "languages.svg").read_text()
        self.assertNotIn("Markdown", svg)
        self.assertIn("L09", svg)

    def test_no_data_exits_nonzero_and_writes_nothing(self):
        out = tempfile.mkdtemp()
        with mock.patch.object(lang.urllib.request, "urlopen", FakeGitHub([page([])])), \
                mock.patch.dict(os.environ, {"GH_TOKEN": "tok"}), mock.patch("sys.argv", ["x", out]):
            with self.assertRaises(SystemExit) as cm:
                lang.main()
        self.assertIn("no language data", str(cm.exception))
        self.assertEqual(os.listdir(out), [])

    def test_missing_token_fails_loudly(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("sys.argv", ["x", "out"]):
            with self.assertRaises(KeyError):
                lang.main()


if __name__ == "__main__":
    unittest.main()
