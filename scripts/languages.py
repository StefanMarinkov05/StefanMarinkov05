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

TOP = 6
# Markup, styles and build files are not "code I write"; same idea as linguist's defaults for profile cards.
SKIP = {"HTML", "CSS", "SCSS", "Less", "Jupyter Notebook", "Makefile", "Dockerfile", "Batchfile",
        "PowerShell", "Procfile", "Blade", "Hack", "Twig", "TeX"}
QUERY = """query($cursor:String){viewer{repositories(first:100, after:$cursor, ownerAffiliations:OWNER, isFork:false){
  pageInfo{hasNextPage endCursor}
  nodes{languages(first:30, orderBy:{field:SIZE, direction:DESC}){edges{size node{name color}}}}}}}"""


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
    w, h = 400, 54 + 22 * ((len(rows) + 1) // 2)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Top languages">',
        f'<rect width="{w}" height="{h}" rx="6" fill="{bg}"/>',
        '<style>text{font:400 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}</style>',
        '<clipPath id="r"><rect x="20" y="18" width="360" height="8" rx="4"/></clipPath>',
        f'<rect x="20" y="18" width="360" height="8" rx="4" fill="{bar_bg}"/>',
        '<g clip-path="url(#r)">',
    ]
    x = 20.0
    for _, pct, color in rows:
        width = 360 * pct / 100
        out.append(f'<rect x="{x:.2f}" y="18" width="{width + 0.5:.2f}" height="8" fill="{color}"/>')
        x += width
    out.append("</g>")
    for i, (name, pct, color) in enumerate(rows):
        cx, cy = 26 + 190 * (i % 2), 50 + 22 * (i // 2)
        out.append(f'<circle cx="{cx}" cy="{cy - 4}" r="5" fill="{color}"/>')
        out.append(f'<text x="{cx + 12}" y="{cy}" fill="{fg}">{escape(name)} <tspan fill="{sub}">{pct:.1f}%</tspan></text>')
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
