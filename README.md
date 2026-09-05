# twin

A config-driven personal site with an AI twin built in. One page — hero, about, career timeline, selected work, contact — plus a docked chat panel that answers visitor questions about my background in my voice.

![The site, with the Digital Twin panel open](assets/screenshot.png)

Everything the site shows, and every colour it uses, comes from a single file: [`profile.yaml`](profile.yaml). Swap that file and the site becomes someone else's — no Python to edit.

## How it works

[`profile.yaml`](profile.yaml) is loaded and validated once at startup by [`profile.py`](profile.py) (pydantic). The resulting `Profile` object feeds three independent, pure modules:

```
profile.yaml ──> profile.py ──> Profile
                                  ├─> sections.py  → HTML per page section
                                  ├─> theme.py     → stylesheet from the palette
                                  └─> context.py   → the twin's system prompt
```

[`app.py`](app.py) assembles those into a `gr.Blocks` page and wires the chat callbacks. It is the only module that imports Gradio; `sections.py` and `theme.py` are pure functions with no I/O, so each is testable on its own.

A section whose config is empty is not rendered at all — a profile with no `portfolio:` simply has no portfolio section.

### The twin

The chat panel is backed by an LLM via [OpenRouter](https://openrouter.ai/). Its system prompt is built from whatever files are listed under `twin.sources`, so adding context is a config change:

```yaml
twin:
  model: openrouter/free
  sources:
    - type: text
      path: summary.txt
    - type: pdf
      path: linkedin.pdf
```

The model can call two tools, defined in [`tools.json`](tools.json), validated by [`tool_loader.py`](tool_loader.py), implemented in [`tools.py`](tools.py):

| Tool | Purpose |
| --- | --- |
| `record_user_details` | Records a visitor's email (and optional name/notes) when they want to be contacted |
| `record_unknown_question` | Records a question the twin couldn't answer |

Both push a notification via [Pushover](https://pushover.net/), so follow-up requests and knowledge gaps arrive in real time. Notifications are best-effort — without the Pushover keys the app still runs.

## Project layout

```
profile.yaml     # All content + palette. Edit this to make the site yours.
profile.py       # Pydantic schema + validating loader for profile.yaml
sections.py      # Pure Profile -> HTML renderers, one per page section
theme.py         # Builds the stylesheet from the configured palette; page JS
context.py       # Builds the twin's system prompt from twin.sources
app.py           # Gradio assembly + chat wiring (only module importing gradio)
tools.py         # Tool implementations
tool_loader.py   # Loads + validates tools.json into OpenAI-style tool schemas
tools.json       # Tool (function-calling) schema definitions
summary.txt      # Short bio, referenced from twin.sources
linkedin.pdf     # LinkedIn export, referenced from twin.sources
assets/          # Profile photo and screenshot
tests/           # pytest suite
```

## Setup

Requires Python 3.13+.

1. Install dependencies:

   ```bash
   uv sync          # reads pyproject.toml / uv.lock
   # or
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root:

   ```
   OPENROUTER_API_KEY=your_openrouter_api_key
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   PUSHOVER_USER=your_pushover_user_key
   PUSHOVER_TOKEN=your_pushover_app_token
   ```

3. Edit [`profile.yaml`](profile.yaml) — identity, palette, about, journey, portfolio, contact, and the twin's model, greeting and example prompts all live there. Point `identity.photo` at your own image in `assets/`, and list your own context files under `twin.sources`.

   Only `identity` and `twin` are required. Every other section is optional and defaults to empty.

## Running

```bash
python app.py
```

Gradio prints a local URL. A bad `profile.yaml` fails here, immediately, naming the offending field — not later, inside a render or an API call.

## Customizing

| What | Where |
| --- | --- |
| Text, sections, links, career entries | `profile.yaml` |
| Colours | `profile.yaml` → `theme:` (8 tokens) |
| Chat examples, greeting, model | `profile.yaml` → `twin:` |
| Prompt context files | `profile.yaml` → `twin.sources` |
| Page markup | `sections.py` |
| Layout and styling | `theme.py` |
| Tools the twin can call | `tools.json` + `tools.py` |

## Testing

```bash
python -m pytest tests/ -v
```

Covers config validation and error messages, HTML escaping and link-scheme allowlisting, palette-to-CSS mapping, and prompt assembly from configured sources.

Tests cannot catch a broken layout, so changes to `sections.py` or `theme.py` are worth confirming in a browser.

## Notes on Gradio 6

This runs on Gradio 6, which differs from most examples online:

- `css`, `js` and `theme` are `launch()` arguments, not `gr.Blocks()` arguments.
- `launch(js=...)` does not execute; page JS is attached with `demo.load(None, None, None, js=JS)`.
- `gr.Chatbot` has no `type=` parameter — history is always `list[dict]`.
- Static files are served from `/gradio_api/file=<path>`, and the directory must be registered with `gr.set_static_paths`.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE).
