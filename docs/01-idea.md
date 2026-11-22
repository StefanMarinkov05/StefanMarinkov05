# 01 - The idea

## Goal

A recruiter or an engineer opens the profile for maybe 30 seconds. In that time the page has to answer
three questions:

1. **What does he do?** The skills card: four areas (Back-end, QA and testing, Security, AI engineering),
   two lines each, nothing that cannot be backed by a project.
2. **Can I see proof?** The projects list: five projects, each folded into a `<details>` block with stack
   tags next to what was built with them.
3. **Is he active?** The languages card and the contribution graph turned into an arcade game.

Everything else is noise and was removed.

## What was dropped, and why

| Removed | Reason |
|---|---|
| "Hi, I'm Stefan" typing banner | The name is already on the profile; the effect reads as "I know this widget exists" |
| City, "open to", English level badges | Personal details that belong on a CV, not on a code profile |
| Wall of technology icons | The most copied block on GitHub; an icon proves only that a tool was heard of. Listing Git or GitHub Actions as a skill reads junior |
| Generic GitHub stats card (stars, commits, rank) | Rank and star counts say little about code; only the language share is about the code itself |
| Phrases that sound written by a model | Rewritten in plain words |

## What was kept or added

- **Skills grouped by capability, not by logo.** A capability ("authorization flaws, injection, webhooks")
  says what I can do; the projects underneath are the evidence.
- **Languages over all repositories.** Most of my code lives in private repositories (university and client
  work). The public-only card showed PHP 52%; the real split is closer to PHP 32%, C# 27%, Python 15%,
  Kotlin 13%. See [05-languages-card.md](05-languages-card.md).
- **One playful element: the Activity game.** The contribution graph is played by an arcade game
  (Snake, Pac-Man, Galaga, Breakout, Puzzle Bobble, Bomberman). A different one on every visit, so a
  second visit shows something new. It is a small easter egg that also shows I can build and deploy a
  service end to end. See [04-random-game-worker.md](04-random-game-worker.md).

## Playground

`scratchpad/README.md` collects every idea that was tried (banners, snake colours, 3D city, stats cards,
joke cards, Mermaid timeline, maps, easter eggs) with a live preview and the code to copy. The profile uses
only a few of them; the rest stay there for experiments.
