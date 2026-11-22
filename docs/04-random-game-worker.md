# 04 - The random game worker (Cloudflare)

Code: `worker/src/index.js`, config: `worker/wrangler.toml`.
Live: https://profile-game.stefanmarinkov.workers.dev

## The problem

GitHub READMEs cannot run JavaScript, and every image is fetched through GitHub's proxy. A static file
always shows the same game. To show a different game per visit, the image URL has to point at something
that answers differently each time: a tiny server.

Options compared:

| Option | Per visit? | Cost | Chosen |
|---|---|---|---|
| Time-based file from the workflow (`floor(t / 3h) mod 6`) | No, same game for everyone for 3 hours | free | fallback only |
| Vercel function | Yes | free hobby plan, slower cold starts | no |
| **Cloudflare Worker** | **Yes** | **free: 100,000 requests a day, runs at the edge, no cold start** | **yes** |

## What the worker does

```js
const names = ["pacman", "galaga", "breakout", "puzzle-bobble", "bomberman", "snake"];
const game  = names[crypto.getRandomValues(new Uint32Array(1))[0] % names.length];
```

1. Reads `?theme=dark` (dark-mode `<source>` in the README) and `?game=<name>` (force one game, for testing).
2. Draws a random 32-bit number from the Web Crypto API and takes it modulo 6.
3. Fetches `<game>-contribution-graph(-dark).svg` (or `github-snake(-dark).svg`) from the `output` branch.
4. Returns it as `image/svg+xml` with `Cache-Control: no-cache, no-store, must-revalidate, max-age=0` and a
   debug header `x-game: <name>`.

## The maths

- **Uniform pick.** Each game has probability 1/6, about 16.7%.
- **Modulo bias.** 2^32 = 4,294,967,296 is not a multiple of 6 (remainder 4), so games 0-3 get one extra
  number out of 4.3 billion. The difference is about 2 x 10^-10: invisible.
- **Repeats.** Two visits in a row show the same game with probability 1/6. Over 10 visits, the chance of
  seeing every one of the six games is about 27%; the expected number of visits to see all six is
  6 x (1 + 1/2 + ... + 1/6) = 14.7 (coupon collector).
- **Sample check (2026-11-22).** 18 direct requests: galaga 6, snake 4, the other four 2 each. All six
  appeared; a chi-square test cannot tell this apart from uniform at n = 18 (too small to say more).

Why not "never the same game twice in a row"? That would need memory per visitor (cookies are not
available through GitHub's proxy). Pure randomness is the honest version.

## Caching, the part that makes it work

There are two caches between a visitor and the worker:

| Cache | What it stores | Setting |
|---|---|---|
| GitHub's image proxy (camo) | the image returned by the worker | obeys `Cache-Control`; `no-store` makes it fetch again on every view |
| Cloudflare edge | the upstream SVG from `raw.githubusercontent.com` | `cf: { cacheTtl: 600 }`: 10 minutes, so most visits never reach GitHub |

So the random choice is never cached, but the six files are. Games are 50-750 KB each; serving them from
Cloudflare's edge keeps the page fast.

Note: browsers may still keep an image in memory while a tab stays open. A real reload (F5) asks again.

## Account and deployment

- Cloudflare account created 2026-11-22 with "Continue with GitHub" (no separate password), free plan.
- Subdomain: `stefanmarinkov.workers.dev`; worker name: `profile-game`.
- Deploy from `worker/`: `npx wrangler@4 deploy`. Login once per machine: `npx wrangler@4 login`.
- The worker has no secrets and no storage. It reads only public files.
