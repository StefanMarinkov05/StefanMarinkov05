"""Top-languages card over ALL owned repos (public and private), forks excluded.

Reads GH_TOKEN (a read-only token that can see the private repos), sums language bytes per
repo via GraphQL and writes two SVGs (dark, light). Only totals are published: no repo names.
Usage: python3 scripts/languages.py OUT_DIR
"""
import json
import os
import sys
import urllib.request
from html import escape

TOP = 10
PYRAMID = [1, 2, 3, 4]  # languages per row, rank 1 on top (1+2+3+4 = TOP, symmetrical)
# Styles and build files are skipped. HTML, TeX and Markdown count (Stefan, 2026-11-28): he writes handbooks and docs too.
SKIP = {"CSS", "SCSS", "Less", "Jupyter Notebook", "Makefile", "Dockerfile", "Batchfile",
        "PowerShell", "Procfile", "Blade", "Hack", "Twig"}
QUERY = """query($cursor:String){viewer{repositories(first:100, after:$cursor, ownerAffiliations:OWNER, isFork:false){
  pageInfo{hasNextPage endCursor}
  nodes{nameWithOwner languages(first:30, orderBy:{field:SIZE, direction:DESC}){edges{size node{name color}}}}}}}"""


def markdown_bytes(token, full_name, branch):
    """GitHub's language data leaves out Markdown (prose), so sum the .md blob sizes of the default branch.
    Needs Contents: read on the token (metadata alone gives 403); on any error this repo adds 0 and the card still builds."""
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{full_name}/git/trees/{branch}?recursive=1",
            headers={"Authorization": f"bearer {token}", "Accept": "application/vnd.github+json"})
        tree = json.load(urllib.request.urlopen(req))["tree"]
    except Exception as e:
        print(f"markdown: skipped one repo ({type(e).__name__})", file=sys.stderr)
        return 0
    return sum(x.get("size", 0) for x in tree if x["type"] == "blob" and x["path"].lower().endswith((".md", ".markdown")))


def fetch(token):
    totals, colors, repos, cursor = {}, {}, 0, None
    while True:
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": QUERY, "variables": {"cursor": cursor}}).encode(),
            headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
        )
        data = json.load(urllib.request.urlopen(req))
        if "errors" in data:
            sys.exit(f"GraphQL error: {data['errors']}")
        page = data["data"]["viewer"]["repositories"]
        for repo in page["nodes"]:
            repos += 1
            md = markdown_bytes(token, repo["nameWithOwner"], "HEAD")  # HEAD = default branch
            if md:
                totals["Markdown"] = totals.get("Markdown", 0) + md
                colors["Markdown"] = "#083fa1"
            for edge in repo["languages"]["edges"]:
                name = edge["node"]["name"]
                if name in SKIP:
                    continue
                totals[name] = totals.get(name, 0) + edge["size"]
                colors[name] = edge["node"]["color"] or "#8b949e"
        if not page["pageInfo"]["hasNextPage"]:
            return totals, colors, repos
        cursor = page["pageInfo"]["endCursor"]


def svg(rows, dark):
    fg, sub, bar_bg, bg = (("#e6edf3", "#8b949e", "#30363d", "#161b22") if dark
                           else ("#1f2328", "#59636e", "#d0d7de", "#f6f8fa"))
    w, h = 460, 44 + 24 * len(PYRAMID)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Top languages">',
        f'<rect width="{w}" height="{h}" rx="6" fill="{bg}"/>',
        '<style>text{font:400 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}</style>',
        '<clipPath id="r"><rect x="20" y="18" width="420" height="8" rx="4"/></clipPath>',
        f'<rect x="20" y="18" width="420" height="8" rx="4" fill="{bar_bg}"/>',
        '<g clip-path="url(#r)">',
    ]
    x = 20.0
    for _, pct, color in rows:
        width = 420 * pct / 100
        out.append(f'<rect x="{x:.2f}" y="18" width="{width + 0.5:.2f}" height="8" fill="{color}"/>')
        x += width
    out.append("</g>")
    i = 0
    for r, n in enumerate(PYRAMID):
        slot = 110
        x0 = 230 - slot * n / 2  # each row centred under the one above
        for c in range(n):
            if i >= len(rows):
                break
            name, pct, color = rows[i]
            cx, cy = x0 + slot * c + 6, 56 + 24 * r
            out.append(f'<circle cx="{cx:.1f}" cy="{cy - 4}" r="5" fill="{color}"/>')
            out.append(f'<text x="{cx + 11:.1f}" y="{cy}" fill="{fg}">{escape(name)} <tspan fill="{sub}">{pct:.1f}%</tspan></text>')
            i += 1
    out.append("</svg>")
    return "\n".join(out)


def main():
    out_dir = sys.argv[1]
    totals, colors, repos = fetch(os.environ["GH_TOKEN"])
    if not totals:
        sys.exit("no language data: does the token see the repositories?")
    total = sum(totals.values())
    top = sorted(totals.items(), key=lambda kv: -kv[1])[:TOP]
    shown = sum(v for _, v in top)
    rows = [(n, 100 * v / shown, colors[n]) for n, v in top]
    os.makedirs(out_dir, exist_ok=True)
    for dark in (True, False):
        with open(os.path.join(out_dir, f"languages{'-dark' if dark else ''}.svg"), "w") as f:
            f.write(svg(rows, dark))
    print(f"{repos} repos, {len(totals)} languages; top {TOP}: "
          + ", ".join(f"{n} {p:.1f}%" for n, p, _ in rows))
    print(f"top {TOP} cover {100 * shown / total:.1f}% of counted bytes")


if __name__ == "__main__":
    main()
