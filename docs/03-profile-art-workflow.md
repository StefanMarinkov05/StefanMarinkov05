# 03 - The profile-art workflow

File: `.github/workflows/profile-art.yml`.

## When it runs

- Every day at 03:00 UTC (`schedule`), so the games follow the newest contributions.
- On every push to `main`, so a change to the README or the scripts shows up at once.
- By hand: Actions tab, "Profile art", "Run workflow" (or `gh workflow run profile-art.yml`).

## Steps

| Step | Tool | Writes |
|---|---|---|
| Snake | `Platane/snk/svg-only@v3` | `github-snake.svg`, `-dark`, `-ocean`, `-lava` |
| Arcade games | `abozanona/pacman-contribution-graph@v5.0.0` | `<game>-contribution-graph(-dark).svg` for pacman, galaga, breakout, puzzle-bobble, bomberman |
| 3D city | `yoshi389111/github-profile-3d-contrib@v0.9.3` | `3d/*.svg` (5 themes) |
| Collect | shell | copies the 3D files, builds the time-based fallback `activity.svg` |
| Languages | `scripts/languages.py` | `languages.svg`, `languages-dark.svg` (only when the `LANG_TOKEN` secret exists) |
| Publish | `crazy-max/ghaction-github-pages@v4` | force-pushes `dist/` to the `output` branch |

The action list also asks for minesweeper, snake and tetris from the arcade action; in v5.0.0 those three
produce no file, so they are not used.

## The fallback Activity image

Before the worker existed, the README showed one game chosen by time:

```
slot = floor(unix_time / 10800) mod 6      # 10800 s = 3 hours
games = [pacman, galaga, breakout, puzzle-bobble, bomberman, snake]
```

The workflow still writes that file as `output/activity.svg` (plus `activity.txt` with the chosen game).
If the Cloudflare Worker ever has to go, point the README back to it.

## Permissions

`contents: write` lets the job push to the `output` branch with the built-in `GITHUB_TOKEN`. The built-in
token sees only this repository, which is why the languages card needs its own token (see
[05-languages-card.md](05-languages-card.md)).
