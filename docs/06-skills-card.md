# 06 - The skills card

Files: `assets/skills-dark.svg` and `assets/skills-light.svg` (900 x 232, hand-written SVG, no tool).

## Design

- A 2 x 2 grid. Each cell has a coloured bar on the left, a title and two lines of keywords.
- Colours follow GitHub's own palette so the card looks native in both themes:

| Area | Dark | Light |
|---|---|---|
| Back-end | #58a6ff | #0969da |
| QA and testing | #3fb950 | #1a7f37 |
| Security | #f85149 | #cf222e |
| AI engineering | #bc8cff | #8250df |
| Background / border | #161b22 / #30363d | #f6f8fa / #d0d7de |

- The README shows it with `<picture>`: the dark file when the viewer uses dark mode, the light file
  otherwise.
- The `alt` text repeats every skill, so screen readers and search engines get the same content.

## Rules for the content

- Capabilities, not logos: "REST APIs, SQL, transactions and locking" rather than icons of tools.
- Every keyword must be backed by a project in the list below the card or by my CV.
- Edit both files when a keyword changes, and keep the `alt` text in `README.md` in sync.
