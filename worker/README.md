# profile-game

Cloudflare Worker behind the README's Activity section: every request returns one of six contribution-graph
games (Snake, Pac-Man, Galaga, Breakout, Puzzle Bobble, Bomberman) at random, with no-cache headers so each
profile visit gets a new pick. The SVGs are generated daily by `.github/workflows/profile-art.yml` into the
`output` branch; the worker only picks and streams one.

- `?theme=dark` serves the dark variant; `?game=<name>` forces one game.
- Deploy: `npx wrangler@4 deploy` from this folder (account login: `npx wrangler@4 login`).
- Live: https://profile-game.stefanmarinkov.workers.dev
