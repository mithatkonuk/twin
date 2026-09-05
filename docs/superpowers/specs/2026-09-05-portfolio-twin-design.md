# Config-driven portfolio page + digital twin

Date: 2026-09-05
Status: approved design, not yet implemented

## Problem

`twin` today is a single `gr.ChatInterface`: one chat box, nothing else. Two
things are wrong with it.

**It is not flexible.** The person it represents is hardcoded across four
files — the title string in `app.py`, the prompt template in `context.py`, the
example prompts and every colour token in `styles.py`, and the literal paths
`linkedin.pdf` / `summary.txt` in `context.py`. Pointing the app at a different
person means editing Python in four places and hoping nothing was missed.

**It is only a chat.** A visitor lands on a terminal-styled box with no context
about who they are talking to. There is no bio, no career history, no project
list, no way to make contact except through the model's tool call.

## Goal

A single-page personal site — hero, About, Journey, Portfolio, Contact — with
the digital twin present as a pinned chat panel, where **every piece of content
and every colour comes from one validated config file**. Swapping
`profile.yaml` swaps the whole site.

## Non-goals

- Multi-page routing, a CMS, or a build step.
- Changing the tool-calling layer (`tools.py`, `tool_loader.py`, `tools.json`).
  It works and is out of scope.
- Light mode. The design is dark-only; a second palette is a later change.
- Authoring real portfolio copy. Journey and Portfolio entries are seeded from
  `linkedin.pdf` and flagged for the owner to correct.

## Architecture

One new data layer feeds three consumers.

```
profile.yaml ──> profile.py (pydantic) ──> Profile
                                             ├─> sections.py  → HTML str → gr.HTML
                                             ├─> theme.py     → CSS str  → gr.Blocks(css=)
                                             └─> context.py   → system prompt → chat()
```

`app.py` shrinks to assembly: load the profile, build the CSS, build the
prompt, lay out the blocks, wire the chat callbacks.

Each module has one job and can be understood without reading the others:

- `profile.py` knows the config schema and nothing about HTML or Gradio.
- `sections.py` is pure `Profile → str`; no I/O, no Gradio import.
- `theme.py` is pure `Theme → str`; no I/O, no Gradio import.
- `context.py` knows how to turn source files into prompt text.
- `app.py` is the only module that imports `gradio`.

This keeps every renderer independently testable and each file small enough to
edit in one pass.

## Components

### `profile.yaml` (new)

Single source of truth. Shape:

```yaml
identity:
  name: Mithat Konuk
  role: Backend Engineer
  location: Munich, Germany
  tagline: >-
    One or two sentences shown under the name in the hero.
  photo: assets/photo.jpg        # optional; initials used if absent

theme:
  bg: "#0A0A0F"
  surface: "#14141C"
  surface_alt: "#1B1B25"
  border: "#26262F"
  text: "#ECECF1"
  muted: "#7C7C8A"
  accent: "#F0B429"
  accent_alt: "#A855F7"

about:
  - First paragraph.
  - Second paragraph.

journey:
  - period: "2025 — present"
    role: Software Engineer
    org: Entirely
    location: Munich, Germany
    detail: What the role involved.
    tags: [Java, R&D]

portfolio:
  - title: Digital Twin
    blurb: One-line description.
    tags: [Python, Gradio, LLM]
    url: https://github.com/...      # optional

contact:
  intro: Optional line above the links.
  links:
    - label: Email
      href: mailto:mithatkonuk@gmail.com
    - label: LinkedIn
      href: https://www.linkedin.com/in/mithat-konuk

twin:
  model: openrouter/free
  heading: Digital Twin
  subheading: Ask about my background
  greeting: Shown in the empty chat panel before the first message.
  examples:
    - Tell me about your background and experience.
  sources:
    - type: text
      path: summary.txt
    - type: pdf
      path: linkedin.pdf
```

### `profile.py` (new)

Pydantic models mirroring the YAML, plus a cached loader. Follows the existing
`tool_loader.py` pattern deliberately — same error philosophy, same
`lru_cache`, so the two loaders read alike.

```python
class Identity(BaseModel): ...
class Theme(BaseModel): ...
class JourneyEntry(BaseModel): ...
class PortfolioEntry(BaseModel): ...
class ContactLink(BaseModel): ...
class Contact(BaseModel):       # intro: str | None, links: list[ContactLink]
class TwinConfig(BaseModel): ...

class Profile(BaseModel):
    identity: Identity
    theme: Theme = Theme()          # every theme field has a default
    about: list[str] = []
    journey: list[JourneyEntry] = []
    portfolio: list[PortfolioEntry] = []
    contact: Contact | None = None
    twin: TwinConfig

@lru_cache(maxsize=1)
def load_profile(path: Path = PROFILE_PATH) -> Profile: ...
```

Only `identity` and `twin` are required. Every list defaults to empty, so a
minimal config produces a valid (shorter) page.

### `theme.py` (replaces `styles.py`)

Exports `build_css(theme: Theme) -> str` and the existing `JS` constant.

The CSS is a module-level template string using `--twin-*` custom properties;
`build_css` emits a `:root { ... }` block from the `Theme` model and
concatenates it with the template. Colours therefore appear in exactly one
place — the config — and the rest of the stylesheet references variables.

Visual direction, replacing the current terminal-window treatment:

| Token | Value | Use |
| --- | --- | --- |
| `bg` | `#0A0A0F` | page ink |
| `surface` | `#14141C` | section cards, chat panel |
| `surface_alt` | `#1B1B25` | message bubbles, tag chips |
| `border` | `#26262F` | hairlines |
| `text` | `#ECECF1` | body |
| `muted` | `#7C7C8A` | eyebrows, meta, timestamps |
| `accent` | `#F0B429` | amber — links, primary button, gradient start |
| `accent_alt` | `#A855F7` | violet — gradient end, secondary marks |

- Name in the hero uses an amber→violet gradient clip.
- A soft radial amber glow sits behind the hero, top-right, at low opacity.
- The faint dot-grid background is kept (it reads well and is already there).
- Dropped: traffic-light dots, blinking caret, forced-square corners,
  uppercase-mono on every button. Those were terminal cosplay and fight the
  portfolio framing. Monospace is retained only for eyebrow labels, tag chips,
  and journey periods.
- Type: Inter for body and headings, JetBrains Mono for the above.
- Radius: 14px on cards, 10px on chips and inputs.

### `sections.py` (new)

One pure function per section, each `Profile → str`, returning the empty string
when the relevant config is empty so the section vanishes rather than rendering
an empty shell:

```python
def render_nav(p: Profile) -> str
def render_hero(p: Profile) -> str
def render_about(p: Profile) -> str
def render_journey(p: Profile) -> str
def render_portfolio(p: Profile) -> str
def render_contact(p: Profile) -> str
def render_footer(p: Profile) -> str
```

All interpolated config values pass through `html.escape`. `href` values are
additionally checked against an allowed-scheme list (`http`, `https`, `mailto`)
so a config cannot inject `javascript:`.

Markup shape:

- **nav** — sticky, section anchors plus a "Digital Twin" link that opens the
  chat panel.
- **hero** — mono eyebrow (`● ABOUT`), gradient `<h1>` name, tagline, round
  photo with a ring; initials fallback when `identity.photo` is unset.
- **about** — a single bordered card, one `<p>` per config paragraph.
- **journey** — vertical timeline: a left rule with a dot per entry; period in
  mono, role + org as the heading, detail below, tag chips.
- **portfolio** — responsive card grid (`auto-fit, minmax(280px, 1fr)`); title,
  blurb, tag chips, optional link.
- **contact** — intro line plus link row.

### `context.py` (rewritten)

`build_system_prompt(profile: Profile) -> str`.

Source loading is dispatched on `type`: `text` reads the file directly, `pdf`
extracts through `pypdf`. Unknown type or missing file raises a message naming
the config index and the path. The prompt template keeps the current rules
(stay in character, career topics only, record email, record unknown questions)
but interpolates `identity.name` instead of a generic phrase, and concatenates
the loaded sources in config order.

### `app.py` (rewritten)

```python
profile = load_profile()
system  = [{"role": "system", "content": build_system_prompt(profile)}]

with gr.Blocks(css=build_css(profile.theme), js=JS, theme=gr.themes.Base()) as demo:
    gr.HTML(render_nav(profile))
    gr.HTML(render_hero(profile))
    gr.HTML(render_about(profile))
    gr.HTML(render_journey(profile))
    gr.HTML(render_portfolio(profile))
    gr.HTML(render_contact(profile))
    with gr.Column(elem_id="twin-panel"):
        chatbot = gr.Chatbot(type="messages", show_label=False)
        msg     = gr.Textbox(...)
        send    = gr.Button(...)
    gr.HTML(render_footer(profile))
```

`chat()` keeps its current logic (tool-calling loop unchanged); `MODEL_NAME`
now comes from `profile.twin.model`.

**Known risk.** `gr.ChatInterface` cannot be nested inside a custom layout, so
the submit/clear glue it provided must be hand-wired: `msg.submit` and
`send.click` both append the user turn, call `chat`, append the reply, and
clear the box. Example prompts become buttons that fill `msg` and submit. This
is the only non-obvious part of the implementation.

The pinned panel is CSS, not Gradio: `#twin-panel` is `position: fixed`,
bottom-right, ~380px wide, open by default, with a header-bar toggle that
collapses it to a pill. Below 768px it becomes a bottom sheet at full width.
The toggle lives in `JS` alongside the existing focus handling.

## Data flow

1. Import time: `load_profile()` reads and validates `profile.yaml`. A bad
   config fails here, loudly, naming the field.
2. `build_system_prompt` reads each configured source once and builds the
   prompt string.
3. `build_css` renders the palette into a `:root` block.
4. Section renderers turn the profile into HTML strings.
5. `gr.Blocks` assembles them; the chat callback runs per message.

Steps 1–4 happen once at startup. Nothing re-reads the config per request.

## Error handling

| Condition | Behaviour |
| --- | --- |
| `profile.yaml` missing | `FileNotFoundError` naming the expected path |
| Malformed YAML | `ValueError` with line/column from the parser |
| Schema violation | `ValueError` wrapping the pydantic error, naming the field |
| `identity.photo` unset or file missing | initials rendered instead; no error |
| Prompt source path missing | `FileNotFoundError` naming the config index and path |
| Unknown source `type` | `ValueError` listing supported types |
| `href` with a disallowed scheme | `ValueError` at render time naming the link |
| Empty `about` / `journey` / `portfolio` / `contact` | section omitted entirely |
| Pushover env vars unset | unchanged — best-effort, app still runs |

## Testing

`pytest`, with `tests/` new to the repo. `pytest` and `pyyaml` join
`requirements.txt` / `pyproject.toml`.

- `test_profile.py` — a minimal config (identity + twin only) loads; the
  shipped `profile.yaml` loads; a field with the wrong type raises a message
  naming that field; a missing file raises naming the path.
- `test_sections.py` — `<script>` in a config value comes out escaped; a
  `javascript:` href is rejected; an empty `journey` list renders `""`; a
  populated one renders one timeline row per entry.
- `test_theme.py` — every `Theme` field appears in the emitted `:root` block;
  no literal hex from the default palette remains in the template body.
- `test_context.py` — the prompt contains the identity name and text from each
  configured source, in config order; an unknown source type raises.

Then a real run (`python app.py`) plus a screenshot to confirm the page renders
as designed — tests cannot catch a broken layout.

## Migration

- `styles.py` is deleted; `theme.py` replaces it.
- `summary.txt` and `linkedin.pdf` stay, but as entries under `twin.sources`
  rather than hardcoded paths.
- `assets/screenshot.png` is regenerated for the README, and the README's
  Project layout, Customizing, and Setup sections are rewritten to describe
  `profile.yaml` as the thing you edit.

## Content seeding

`linkedin.pdf` contains a real, usable history — Entirely (2025–present),
censhare (2021–2025), Sqills (2021), sahibinden.com (2018–2021), NETAŞ
(2014–2018), plus a summary paragraph and contact details. The initial
`profile.yaml` is populated from it. Journey and Portfolio entries carry a
`# review:` comment where wording was inferred, so the owner can correct them
rather than the design inventing a career.

## Open questions

None blocking. Light mode, i18n, and a real project list are deliberately
deferred.
