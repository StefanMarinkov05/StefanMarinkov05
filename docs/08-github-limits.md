# 08 - What a GitHub README can and cannot do

GitHub sanitises README HTML. Knowing the rules explains most design choices in this repository.

## Not allowed (stripped silently)

- `<style>` blocks, `style="..."` attributes, `<link>` stylesheets: no custom CSS on the profile.
- `<script>` and event handlers (`onclick` ...): no JavaScript.
- `<iframe>`, forms, custom fonts.
- There is no setting for a custom profile theme, banner or background, and no way to import a template.

## Allowed, and used here

| Feature | Where |
|---|---|
| Images, including SVG with its own internal CSS and animation | every card and game |
| `<picture>` + `prefers-color-scheme` | dark and light versions of each card |
| `<details>` / `<summary>` | the folded project list |
| `align`, `width`, `height` attributes | centring and sizing |
| Images served by any HTTPS server | the random game worker |

An SVG loaded as an image can animate (CSS keyframes, SMIL) but cannot run scripts or load other files,
so everything an SVG shows must be inside the file. That is why the games are pre-drawn SVGs and the
worker only picks one.

## Also allowed (tried in `scratchpad/`)

- Mermaid diagrams, GeoJSON maps, STL 3D models, maths (`$...$`), alerts (`> [!NOTE]`), `<kbd>`.
- Hidden easter eggs: an HTML comment visible only in the source, a different message in light and dark
  mode via `<picture>`, a tooltip in an image `title`.
