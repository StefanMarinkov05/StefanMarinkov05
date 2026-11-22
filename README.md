# Stefan Marinkov

Computer science student at Saarland University (B.Sc., expected 2027), building software since 2021.
I take the parts where a bug costs money or trust: payments, stock locking and authorization in web
apps, and defences that keep AI agents from being steered by text hidden in documents.

Saarbrücken, Germany | Bulgarian (native), English (C1)

## Featured work

| Project | What it is | Evidence |
|---|---|---|
| [injection-guard](https://github.com/StefanMarinkov05/injection-guard) | Protects AI coding agents from prompt injection: agent hooks plus a scanner for PDF, Office, HTML, email and images (Python) | Red-team bench of 60 attacks with harmless twins, 410 real agent runs, 495 tests in CI, a 20-page paper. A fake correction notice fooled 9 of 9 agents; my added check brought it to 0 of 9 |
| [Genesis](https://github.com/StefanMarinkov05/genesis_v6-lite) | Turns a JSON spec into a buildable, seeded ASP.NET Core MVC app; the code comes from a deterministic generator, not the model (C#, TypeScript) | Nine-stage resumable pipeline, each code stage gated by a build; the verify stage boots the app and checks every route and access rule. 191 tests, 15 ADRs |
| [Amazoff](https://github.com/StefanMarinkov05/Amazoff-PHP) | Laravel online shop from my internship at Lumen101, two-person team (PHP) | My parts: database locking on stock, coupons and orders; Stripe webhooks that never charge twice; a closed authorization bypass, each fix with a test that fails without it; 21 of the shop's 25 decisions documented as ADRs |
| [AI development setup](https://github.com/StefanMarinkov05/claude-config-public) | Reusable skills, rules and hooks that keep AI coding agents inside a project's decisions (Shell) | Hooks block unsafe agent behaviour, for example reading .env, so credentials never reach transcripts or logs |
| [.NET E-Commerce Store](https://github.com/StefanMarinkov05/E-commerce) | Online store with clean architecture (C#, ASP.NET Core, SQL Server) | Diploma project for my vocational qualification (SoftUni) |

## Skills

- **Languages:** C#, PHP, Python, TypeScript, Kotlin, Java, SQL
- **Backend and data:** ASP.NET Core, Laravel, Django, REST APIs, relational schema design, transactions and locking
- **Quality and security:** automated tests from unit to system level, Playwright, load testing, WCAG 2.1 AA audits, application security, CTF and binary exploitation
- **AI engineering:** Claude Code skills, hooks and MCP, prompt engineering, LLM evaluation
- **Delivery:** Git and pull-request review, Docker, GitHub Actions, Linux

## How I work

I write the intent before an AI agent codes, record every decision as an ADR, review the result by hand,
and add a regression test for every fix.
