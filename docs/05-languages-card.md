# 05 - The languages card (public and private repositories)

Code: `scripts/languages.py`. Output: `output/languages.svg` and `output/languages-dark.svg`.

## Why not the usual card

The common `github-readme-stats` card runs on a shared public server with its own token, so it can only
see public repositories. Most of my code is private (university group projects, client work), so the
public card was wrong:

| | Public only | Public + private (2026-11-22) |
|---|---|---|
| 1 | PHP 51.6% | PHP 32.3% |
| 2 | C# 23.5% | C# 27.2% |
| 3 | Python 16.4% | Python 15.3% |
| 4 | TypeScript 7.7% | Kotlin 13.2% |
| 5 | JavaScript 0.4% | Scala 6.9% |
| 6 | Shell 0.4% | TypeScript 5.1% |

## How it counts

1. One GraphQL query, paged 100 at a time: every repository I own (`ownerAffiliations: OWNER`), forks
   excluded (`isFork: false`), with its languages and their sizes in bytes (GitHub Linguist).
   On 2026-11-22 that is 40 of my 45 repositories; the other 5 are forks of other people's projects
   (cellular-automaton.nvim, Awesome-GPT-Agents, Supreme, heartbeat, SQL-Injection-cheat-sheet), whose
   code I did not write.
2. Sums bytes per language across all repositories.
3. Leaves out markup, styles, build files and documents: HTML, CSS, SCSS, Less, Jupyter Notebook, Makefile,
   Dockerfile, Batchfile, PowerShell, Procfile, Blade, Hack, Twig, TeX. They inflate the numbers without
   being the code a reader cares about (TeX alone was 7%: my LaTeX handbooks).
4. Takes the top 6 and shows each as a share of those 6 (they cover about 92% of the counted bytes).
5. Draws a dark and a light SVG in GitHub's colours; the README picks one with `<picture>` and
   `prefers-color-scheme`.

Bytes are a rough measure: a generated file or a vendored library counts as much as hand-written code.
Linguist already skips most vendored and generated files.

## What is published

Only the six language names and their percentages. No repository names, no file names, no code.

## The token

- Secret `LANG_TOKEN` in this repository (Settings, Secrets and variables, Actions).
- Fine-grained personal access token `profile-languages`: repository access "All repositories",
  permission **Metadata: read-only** and nothing else; no expiration.
- Metadata read lets it list repositories and read their language sizes. It cannot read file contents,
  push, open issues or change settings.
- The workflow step is skipped when the secret is missing, so the job never fails because of it.

Pitfall met on 2026-11-22: choosing "All repositories" without adding any permission saved the token with
**no repository access** (it then counted only 10 public repositories). Adding "Metadata" explicitly fixed
it (40 repositories counted).
