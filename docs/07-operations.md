# 07 - Operations

## Everyday changes

| I want to... | Do this |
|---|---|
| change text on the profile | edit `README.md` (in the GitHub web editor or locally); push or merge to `main` |
| change a skill keyword | edit both `assets/skills-*.svg` and the `alt` text in `README.md` |
| redraw everything now | Actions, "Profile art", "Run workflow" (or `gh workflow run profile-art.yml`) |
| add or remove a game from the random pick | edit `GAMES` in `worker/src/index.js`, then `npx wrangler@4 deploy` in `worker/` |
| force one game (testing) | open `https://profile-game.stefanmarinkov.workers.dev/?game=galaga` |
| see which game was picked | `curl -sI https://profile-game.stefanmarinkov.workers.dev/ \| grep x-game` |
| try a new design | add it to `scratchpad/README.md` first, move it to the profile when it works |

All changes go through a short branch and a pull request that is merged right away: the history stays
readable and every merged PR counts toward the Pull Shark achievement.

## When something breaks

| Symptom | Likely cause | Fix |
|---|---|---|
| Activity image broken | worker down or deleted, or `output` branch missing the file | `curl -I` the worker URL; redeploy; or point the README to `output/activity.svg` (time-based fallback) |
| Activity always shows the same game | a cache kept the image | check the worker still sends `Cache-Control: no-store`; hard reload |
| Languages card shows only public numbers | `LANG_TOKEN` lost its repository access | token settings: "All repositories" + "Metadata: read-only"; rerun the workflow and check the log line `N repos` |
| Languages card missing | secret deleted, step skipped | recreate the token and the secret (see 05) |
| Games stop updating | workflow failing | Actions tab, open the last red run |
| Images outdated after a change | GitHub's proxy caches static images for a while | wait a few minutes or reload with cache cleared |

## Limits and costs

| Part | Plan | Limit | Use today |
|---|---|---|---|
| GitHub Actions | free (public repository) | unlimited minutes for public repositories | about 2 minutes a day |
| Cloudflare Workers | free | 100,000 requests a day, 10 ms CPU per request | one request per profile view |
| raw.githubusercontent.com | free | rate limits on heavy use | shielded by Cloudflare's 10-minute edge cache |

Nothing here costs money. No payment method is stored on the Cloudflare account.

## Credentials

| Credential | Where | Scope | Rotation |
|---|---|---|---|
| `LANG_TOKEN` | repository Actions secret | fine-grained, all repositories, Metadata read-only | no expiration; regenerate on GitHub and update the secret if it ever leaks |
| Wrangler login | `~/.config/.wrangler/` on my laptop | deploy workers to my Cloudflare account | `npx wrangler@4 logout` / `login`; revoke in Cloudflare, My Profile, Access Management |
| `GITHUB_TOKEN` | built into Actions | this repository only | automatic |
