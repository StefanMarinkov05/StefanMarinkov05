# How this profile works

This repository is my GitHub profile page. GitHub shows `README.md` of the repository named like the
account on the profile itself. Everything else in the repository exists to feed that one page.

| Document | What it explains |
|---|---|
| [01-idea.md](01-idea.md) | Why the profile looks the way it does: the goal, what was kept, what was dropped and why |
| [02-architecture.md](02-architecture.md) | The moving parts and how a profile visit turns into pictures (diagram) |
| [03-profile-art-workflow.md](03-profile-art-workflow.md) | The daily GitHub Actions job that draws the games and the 3D city |
| [04-random-game-worker.md](04-random-game-worker.md) | The Cloudflare Worker that picks a random game on every visit, and the maths behind it |
| [05-languages-card.md](05-languages-card.md) | The top-languages card that counts private repositories too, and the token behind it |
| [06-skills-card.md](06-skills-card.md) | The hand-drawn skills card at the top |
| [07-operations.md](07-operations.md) | How to change, redeploy, rotate, debug; limits and costs |
| [08-github-limits.md](08-github-limits.md) | What a GitHub README can and cannot do (no CSS, no JavaScript) and the workarounds used here |

Folder map:

```
README.md                         the profile page itself
assets/skills-{dark,light}.svg    skills card (hand-written SVG)
.github/workflows/profile-art.yml daily job: games, 3D city, languages card -> `output` branch
scripts/languages.py              top-languages card over public + private repositories
worker/                           Cloudflare Worker: random game per visit
scratchpad/                       playground with every design idea, live previews and copy-paste code
docs/                             this documentation
output (branch)                   generated SVGs, rewritten by the workflow; never edit by hand
```
