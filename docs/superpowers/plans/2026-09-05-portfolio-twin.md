# Config-driven Portfolio Page + Digital Twin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the single-chat Gradio app into a one-page personal site — hero, About, Journey, Portfolio, Contact, plus a pinned Digital Twin chat panel — where all content and all colours come from one validated `profile.yaml`.

**Architecture:** `profile.yaml` → `profile.py` (pydantic, validated at import) → a `Profile` object consumed by three pure modules: `sections.py` (`Profile → HTML str`), `theme.py` (`Theme → CSS str`), and `context.py` (`Profile → system prompt`). `app.py` is the only module importing `gradio`; it assembles those strings into a `gr.Blocks` and hand-wires the chat callbacks.

**Tech Stack:** Python 3.13, Gradio 6.26, pydantic 2.13, PyYAML 6.0, pypdf, openai (OpenRouter), pytest.

**Spec:** `docs/superpowers/specs/2026-09-05-portfolio-twin-design.md`

## Global Constraints

- Python `>=3.13`. Run everything through the project venv: `.venv/bin/python`, `.venv/bin/pytest`.
- **Gradio 6 API — do not use Gradio 4/5 idioms.** Verified on the installed 6.26.0:
  - `css`, `js`, `theme` are **`launch()`** arguments, NOT `gr.Blocks()` arguments.
  - `gr.Chatbot` has **no `type=` parameter** in v6; history is always `list[dict]` with `role`/`content` keys.
  - `gr.Blocks.__init__` accepts only: `analytics_enabled, mode, title, fill_height, fill_width, delete_cache`.
- `tools.py`, `tool_loader.py`, `tools.json` are **out of scope** — do not modify them.
- Only `app.py` may `import gradio`. `sections.py`, `theme.py`, `profile.py`, `context.py` must import no Gradio.
- `sections.py` and `theme.py` are pure: no file I/O, no network, no environment reads.
- Every config-supplied string interpolated into HTML goes through `esc()`. Every `href` goes through `safe_href()`.
- Dark palette only. No light-mode CSS. Palette tokens, verbatim:
  `bg #0A0A0F`, `surface #14141C`, `surface_alt #1B1B25`, `border #26262F`, `text #ECECF1`, `muted #7C7C8A`, `accent #F0B429`, `accent_alt #A855F7`.
- CSS custom properties are namespaced `--tw-*`. CSS class names are namespaced `tw-`.
- Commit after every task. Conventional-commit prefixes (`feat:`, `test:`, `docs:`, `refactor:`, `chore:`).

---

## File Structure

| File | Status | Responsibility |
| --- | --- | --- |
| `profile.yaml` | create | All content + palette. The only file you edit to re-skin or re-person the site. |
| `profile.py` | create | Pydantic models + cached loader. Knows the config schema; knows nothing about HTML or Gradio. |
| `sections.py` | create | Pure `Profile → HTML str` renderers, one per page section, plus `esc`/`safe_href`. |
| `theme.py` | create | Pure `Theme → CSS str` builder over a static template, plus the `JS` constant. Replaces `styles.py`. |
| `context.py` | rewrite | Loads configured prompt sources (text/pdf) and builds the system prompt. |
| `app.py` | rewrite | Gradio assembly + hand-wired chat callbacks. Only Gradio importer. |
| `styles.py` | delete | Superseded by `theme.py`. |
| `tests/test_profile.py` | create | Loader + validation behaviour. |
| `tests/test_sections.py` | create | Escaping, href allowlist, empty-section omission, row counts. |
| `tests/test_theme.py` | create | Every token emitted; no stray literal hex in the template body. |
| `tests/test_context.py` | create | Source dispatch, ordering, error messages. |
| `README.md` | rewrite | Describe `profile.yaml` as the thing you edit. |

---

## Task 1: Config schema and loader

**Files:**
- Create: `profile.py`
- Create: `tests/test_profile.py`
- Modify: `requirements.txt`, `pyproject.toml`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `PROFILE_PATH: Path` — `Path(__file__).parent / "profile.yaml"`
  - `load_profile(path: Path = PROFILE_PATH) -> Profile` — cached, validating
  - Models: `Identity`, `Theme`, `JourneyEntry`, `PortfolioEntry`, `ContactLink`, `Contact`, `Source`, `TwinConfig`, `Profile`
  - Field names exactly as written in the code below — Tasks 2–7 index into these.

- [ ] **Step 1: Add dependencies**

`requirements.txt` becomes:

```
requests
gradio
pypdf
openai
python-dotenv
pyyaml
pytest
```

`pyproject.toml` — replace the empty `dependencies = []` line:

```toml
dependencies = [
    "requests",
    "gradio",
    "pypdf",
    "openai",
    "python-dotenv",
    "pyyaml",
]

[dependency-groups]
dev = ["pytest"]
```

Then run: `.venv/bin/python -m pip install pyyaml pytest`
Expected: both already present or installed cleanly.

- [ ] **Step 2: Write the failing tests**

Create `tests/test_profile.py`:

```python
from pathlib import Path

import pytest
import yaml

from profile import Profile, load_profile

MINIMAL = {
    "identity": {"name": "Ada Lovelace", "role": "Engineer"},
    "twin": {"model": "openrouter/free", "sources": []},
}


def write(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "profile.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_minimal_config_loads(tmp_path):
    profile = load_profile(write(tmp_path, MINIMAL))
    assert isinstance(profile, Profile)
    assert profile.identity.name == "Ada Lovelace"


def test_optional_sections_default_to_empty(tmp_path):
    profile = load_profile(write(tmp_path, MINIMAL))
    assert profile.about == []
    assert profile.journey == []
    assert profile.portfolio == []
    assert profile.contact is None


def test_theme_defaults_to_the_dark_palette(tmp_path):
    profile = load_profile(write(tmp_path, MINIMAL))
    assert profile.theme.bg == "#0A0A0F"
    assert profile.theme.accent == "#F0B429"
    assert profile.theme.accent_alt == "#A855F7"


def test_theme_field_can_be_overridden(tmp_path):
    data = {**MINIMAL, "theme": {"accent": "#FF0000"}}
    profile = load_profile(write(tmp_path, data))
    assert profile.theme.accent == "#FF0000"
    assert profile.theme.bg == "#0A0A0F"


def test_journey_entry_is_parsed(tmp_path):
    data = {
        **MINIMAL,
        "journey": [
            {
                "period": "2025 — present",
                "role": "Software Engineer",
                "org": "Entirely",
                "detail": "R&D team.",
                "tags": ["Java"],
            }
        ],
    }
    profile = load_profile(write(tmp_path, data))
    assert profile.journey[0].org == "Entirely"
    assert profile.journey[0].tags == ["Java"]


def test_missing_required_field_names_the_field(tmp_path):
    data = {"identity": {"role": "Engineer"}, "twin": {"sources": []}}
    with pytest.raises(ValueError) as exc:
        load_profile(write(tmp_path, data))
    assert "identity" in str(exc.value)
    assert "name" in str(exc.value)


def test_wrong_type_names_the_field(tmp_path):
    data = {**MINIMAL, "journey": "not a list"}
    with pytest.raises(ValueError) as exc:
        load_profile(write(tmp_path, data))
    assert "journey" in str(exc.value)


def test_missing_file_names_the_path(tmp_path):
    missing = tmp_path / "nope.yaml"
    with pytest.raises(FileNotFoundError) as exc:
        load_profile(missing)
    assert "nope.yaml" in str(exc.value)


def test_malformed_yaml_reports_position(tmp_path):
    path = tmp_path / "profile.yaml"
    path.write_text("identity: [unclosed\n", encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        load_profile(path)
    assert "profile.yaml" in str(exc.value)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_profile.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'profile'` (or a stdlib `profile` module with no `load_profile`).

> Note: Python has a stdlib module named `profile`. Because the app runs from the project root, the local `profile.py` shadows it. This is intentional and matches the spec. If any test collection error mentions the stdlib profiler, confirm you are running pytest from the project root.

- [ ] **Step 4: Write the implementation**

Create `profile.py`:

```python
"""Load and validate the site profile — the single source of content and colour.

Everything the page shows and every colour it uses comes from `profile.yaml`.
Swapping that file swaps the whole site. Validation happens once, at import,
so a typo surfaces on startup with the field named rather than as a confusing
failure deep inside a render or an API call.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ValidationError

PROFILE_PATH = Path(__file__).parent / "profile.yaml"


class Identity(BaseModel):
    name: str
    role: str
    location: str | None = None
    tagline: str | None = None
    photo: str | None = None


class Theme(BaseModel):
    """Palette tokens. Every field has a default, so `theme:` may be omitted."""

    bg: str = "#0A0A0F"
    surface: str = "#14141C"
    surface_alt: str = "#1B1B25"
    border: str = "#26262F"
    text: str = "#ECECF1"
    muted: str = "#7C7C8A"
    accent: str = "#F0B429"
    accent_alt: str = "#A855F7"


class JourneyEntry(BaseModel):
    period: str
    role: str
    org: str
    location: str | None = None
    detail: str | None = None
    tags: list[str] = []


class PortfolioEntry(BaseModel):
    title: str
    blurb: str
    tags: list[str] = []
    url: str | None = None


class ContactLink(BaseModel):
    label: str
    href: str


class Contact(BaseModel):
    intro: str | None = None
    links: list[ContactLink] = []


class Source(BaseModel):
    """A file feeding the twin's prompt context."""

    type: Literal["text", "pdf"]
    path: str


class TwinConfig(BaseModel):
    model: str = "openrouter/free"
    heading: str = "Digital Twin"
    subheading: str | None = None
    greeting: str | None = None
    examples: list[str] = []
    sources: list[Source] = []


class Profile(BaseModel):
    identity: Identity
    twin: TwinConfig
    theme: Theme = Theme()
    about: list[str] = []
    journey: list[JourneyEntry] = []
    portfolio: list[PortfolioEntry] = []
    contact: Contact | None = None


def _load_raw(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Profile config not found: {path}") from None

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ValueError(f"Malformed YAML in {path}: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping at the top level of {path}, got {type(data).__name__}")
    return data


@lru_cache(maxsize=1)
def load_profile(path: Path = PROFILE_PATH) -> Profile:
    """Read, validate, and cache the profile.

    Raises FileNotFoundError (no file), or ValueError for malformed YAML and
    for schema violations — the latter wrapping pydantic's error, which names
    the offending field path.
    """
    raw = _load_raw(path)
    try:
        return Profile(**raw)
    except ValidationError as e:
        raise ValueError(f"Invalid profile config in {path}:\n{e}") from e
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_profile.py -v`
Expected: 9 passed.

- [ ] **Step 6: Commit**

```bash
git add profile.py tests/test_profile.py requirements.txt pyproject.toml
git commit -m "feat: add validated profile.yaml config loader"
```

---

## Task 2: Seed the real profile.yaml

**Files:**
- Create: `profile.yaml`
- Modify: `tests/test_profile.py` (append one test)

**Interfaces:**
- Consumes: `load_profile`, `PROFILE_PATH` from Task 1.
- Produces: a `profile.yaml` at the repo root that every later task loads.

Content comes from `linkedin.pdf` (real career history) and `summary.txt`. Entries where wording was inferred rather than quoted carry a `# review:` comment for the owner to correct.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_profile.py`:

```python
def test_shipped_profile_loads():
    from profile import PROFILE_PATH

    profile = load_profile(PROFILE_PATH)
    assert profile.identity.name
    assert profile.journey, "expected seeded journey entries"
    assert profile.twin.sources, "expected seeded prompt sources"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_profile.py::test_shipped_profile_loads -v`
Expected: FAIL — `FileNotFoundError: Profile config not found: .../profile.yaml`

- [ ] **Step 3: Create profile.yaml**

```yaml
# Everything this site shows comes from this file. Swap it to swap the site.
# Lines marked "# review:" were inferred from linkedin.pdf — correct them.

identity:
  name: Mithat Konuk
  role: Backend Engineer
  location: Munich, Germany
  tagline: >-
    Software engineer with 10+ years building APIs, distributed systems and
    high-throughput services in Java and the JVM ecosystem. Strong focus on
    design elegance, software reuse, and open source.
  photo: assets/photo.jpg

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
  - >-
    I have spent over ten years across the whole software lifecycle — creating
    APIs and features, architecting and implementing object-oriented and
    distributed systems, working directly with customers, and designing and
    analysing algorithms.
  - >-
    My work has centred on high-throughput web applications and system design:
    Spring and Quarkus services, microservices and containerisation, and the
    messaging and storage layers underneath them. I care about API design,
    systems architecture, and concurrent systems.
  - >-
    I am originally from Türkiye and moved to Germany in 2021. I am a friendly
    communicator, a hard worker, and happy to take responsibility for the
    things I build.

journey:
  - period: "2025 — present"
    role: Software Engineer
    org: Entirely
    location: Munich, Germany
    detail: >-
      Part of the R&D team at Entirely — an open marketing-technology ecosystem
      founded by Marmind, censhare, Elaine and Facelift — held alongside my
      senior developer role at censhare.
    tags: [R&D, Martech]

  - period: "2021 — 2025"
    role: Back End Developer
    org: censhare
    location: Munich, Germany
    detail: >-
      Core team, working across DAM, CMS and content management.
    tags: [Java, DAM, CMS]

  - period: "2021"
    role: Software Craftsman
    org: Sqills
    location: Amsterdam, Netherlands
    detail: >-
      Improved the architecture of in-house IT solutions for the S3 Passenger
      suite — seat reservation, ticketing, distribution and revenue management
      for rail and bus operators. Converted a monolith into maintainable
      containerised microservices and introduced application metrics and
      monitoring with alerting on defined violations.
    tags: [Java, Microservices, Docker]

  - period: "2018 — 2021"
    role: Software Craftsman
    org: sahibinden.com
    location: Istanbul, Türkiye
    detail: >-
      Built a store warning system and an auctions acceptance system for
      Türkiye's largest online classifieds site — 10 Gbps+ peak traffic,
      1.5 billion monthly page views, 43 million monthly unique visitors.
    tags: [Java 11, Kotlin, Spring Boot, Cassandra, Spark, Redis]

  - period: "2014 — 2018"
    role: Senior Software Engineer
    org: NETAŞ
    location: Istanbul, Türkiye
    detail: >-
      V-Gate VoIP security platform (fraud and network attack protection), a
      license management system, and a mediation data-flow service collecting
      and encrypting customer telecommunication data over Kafka and ZooKeeper
      channels — full responsibility for its design, implementation and testing.
      Earlier, a OneM2M telecommunication gateway in C/C++/Java, converting CoAP
      to bidirectional HTTP.
    tags: [Java EE, Spring Boot, Kafka, ZooKeeper, PostgreSQL]

  - period: "2013 — 2014"
    role: Software Engineer
    org: PHI Tech Bioinformatics / Globit
    location: Istanbul, Türkiye
    detail: >-
      Implemented the BLAST algorithm for protein and human DNA sequence
      comparison, published in Oxford Bioinformatics. Also built a SaaS
      timesheet application and a license management system at Globit.
    tags: [Java, Algorithms, PostgreSQL]

# review: these are placeholders — replace with the projects you want to show.
portfolio:
  - title: Digital Twin
    blurb: >-
      This site's AI twin — a config-driven Gradio app that answers questions
      about my background, with tool calls for contact capture and unanswered
      questions.
    tags: [Python, Gradio, LLM, OpenRouter]
    url: https://github.com/mko/twin

  - title: Phisto
    blurb: >-
      Pathogen–host interaction search tool. BLAST-based sequence comparison,
      published in Oxford Bioinformatics.
    tags: [Java, Bioinformatics, Algorithms]
    url: https://academic.oup.com/bioinformatics/article/29/10/1357/257455

  - title: Mediation Data Flow
    blurb: >-
      Telecommunication data collection platform — an API-gateway mediation
      server plus on-premise agents streaming encrypted data over dedicated
      Kafka channels with pluggable adapters and converters.
    tags: [Java Core, Kafka, ZooKeeper, PostgreSQL]

contact:
  intro: >-
    Happy to talk about backend work, distributed systems, or anything you read
    above. The twin can also take your details and pass them along.
  links:
    - label: Email
      href: mailto:mithatkonuk@gmail.com
    - label: LinkedIn
      href: https://www.linkedin.com/in/mithat-konuk

twin:
  model: openrouter/free
  heading: Digital Twin
  subheading: Ask about my career
  greeting: >-
    I can answer questions about Mithat's background, roles, and technical
    experience, grounded in what is on this site.
  examples:
    - Tell me about your background and experience.
    - What kinds of systems have you built at scale?
    - What are your strongest technical skills?
    - How can I get in touch with you?
  sources:
    - type: text
      path: summary.txt
    - type: pdf
      path: linkedin.pdf
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_profile.py -v`
Expected: 10 passed.

- [ ] **Step 5: Commit**

```bash
git add profile.yaml tests/test_profile.py
git commit -m "feat: seed profile.yaml from linkedin export"
```

---

## Task 3: Section renderers — helpers, nav, hero, about

**Files:**
- Create: `sections.py`
- Create: `tests/test_sections.py`

**Interfaces:**
- Consumes: `Profile` and its models from Task 1.
- Produces (Tasks 4, 5 and 7 depend on these exact names):
  - `esc(value: object) -> str`
  - `safe_href(href: str) -> str` — raises `ValueError` on a disallowed scheme
  - `render_nav(p: Profile) -> str`
  - `render_hero(p: Profile) -> str`
  - `render_about(p: Profile) -> str`
  - **CSS class contract** (Task 5 styles exactly these; do not rename):
    `tw-nav`, `tw-nav__inner`, `tw-nav__brand`, `tw-nav__links`, `tw-nav__link`,
    `tw-hero`, `tw-hero__glow`, `tw-hero__text`, `tw-hero__eyebrow`,
    `tw-hero__name`, `tw-hero__role`, `tw-hero__tagline`, `tw-hero__photo`,
    `tw-hero__initials`, `tw-section`, `tw-section__eyebrow`,
    `tw-section__title`, `tw-card`, `tw-prose`
  - **Section anchor ids**: `about`, `journey`, `portfolio`, `contact`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_sections.py`:

```python
import pytest

from profile import Contact, ContactLink, Identity, Profile, TwinConfig
from sections import esc, render_about, render_hero, render_nav, safe_href


def make_profile(**overrides) -> Profile:
    base = {
        "identity": Identity(name="Ada Lovelace", role="Engineer"),
        "twin": TwinConfig(),
    }
    return Profile(**{**base, **overrides})


def test_esc_neutralises_markup():
    assert esc("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"


def test_esc_escapes_quotes_for_attribute_context():
    assert '"' not in esc('a "quoted" value')


def test_esc_renders_none_as_empty_string():
    assert esc(None) == ""


@pytest.mark.parametrize("href", ["https://x.dev", "http://x.dev", "mailto:a@b.dev"])
def test_safe_href_allows_expected_schemes(href):
    assert safe_href(href) == esc(href)


@pytest.mark.parametrize("href", ["javascript:alert(1)", "data:text/html,x", "file:///etc/passwd"])
def test_safe_href_rejects_other_schemes(href):
    with pytest.raises(ValueError) as exc:
        safe_href(href)
    assert href in str(exc.value)


def test_hero_shows_name_role_and_tagline():
    p = make_profile(identity=Identity(name="Ada", role="Engineer", tagline="Builds engines."))
    html = render_hero(p)
    assert "Ada" in html
    assert "Engineer" in html
    assert "Builds engines." in html


def test_hero_escapes_injected_markup():
    p = make_profile(identity=Identity(name="<img onerror=x>", role="Engineer"))
    assert "<img" not in render_hero(p)


def test_hero_falls_back_to_initials_without_a_photo():
    p = make_profile(identity=Identity(name="Ada Lovelace", role="Engineer"))
    html = render_hero(p)
    assert "tw-hero__initials" in html
    assert ">AL<" in html


def test_hero_uses_an_img_when_a_photo_is_configured():
    p = make_profile(identity=Identity(name="Ada", role="Engineer", photo="assets/photo.jpg"))
    html = render_hero(p)
    assert "<img" in html
    assert "assets/photo.jpg" in html


def test_about_renders_one_paragraph_per_entry():
    p = make_profile(about=["First.", "Second."])
    html = render_about(p)
    assert html.count("<p") == 2
    assert 'id="about"' in html


def test_about_is_empty_when_unconfigured():
    assert render_about(make_profile()) == ""


def test_nav_links_only_to_populated_sections():
    p = make_profile(about=["x"])
    html = render_nav(p)
    assert 'href="#about"' in html
    assert 'href="#journey"' not in html
    assert 'href="#portfolio"' not in html


def test_nav_always_offers_the_twin():
    assert "twin-panel-open" in render_nav(make_profile())
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_sections.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sections'`

- [ ] **Step 3: Write the implementation**

Create `sections.py`:

```python
"""Pure renderers turning a Profile into HTML fragments.

Every function here is `Profile -> str` with no I/O and no Gradio import, so
each is testable on its own. A section whose config is empty renders the empty
string — the page simply does not show it, rather than showing an empty shell.

All config-supplied text passes through `esc`, and every link through
`safe_href`; a profile.yaml is content, not code, and must not be able to
inject script.
"""

from __future__ import annotations

import html

from profile import Profile

ALLOWED_SCHEMES = ("https://", "http://", "mailto:")


def esc(value: object) -> str:
    """Escape a config value for use in HTML text or a quoted attribute."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def safe_href(href: str) -> str:
    """Escape a URL, rejecting any scheme that could execute."""
    if not href.startswith(ALLOWED_SCHEMES):
        allowed = ", ".join(ALLOWED_SCHEMES)
        raise ValueError(f"Unsupported link scheme in {href!r}. Allowed prefixes: {allowed}")
    return esc(href)


def _initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    return "".join(p[0].upper() for p in parts[:2])


def _eyebrow(label: str) -> str:
    return f'<span class="tw-section__eyebrow">{esc(label)}</span>'


def render_nav(p: Profile) -> str:
    links = []
    if p.about:
        links.append('<a class="tw-nav__link" href="#about">About</a>')
    if p.journey:
        links.append('<a class="tw-nav__link" href="#journey">Journey</a>')
    if p.portfolio:
        links.append('<a class="tw-nav__link" href="#portfolio">Portfolio</a>')
    if p.contact and p.contact.links:
        links.append('<a class="tw-nav__link" href="#contact">Contact</a>')
    links.append(
        '<a class="tw-nav__link tw-nav__link--cta" href="#" id="twin-panel-open">'
        f"{esc(p.twin.heading)}</a>"
    )
    return (
        '<nav class="tw-nav"><div class="tw-nav__inner">'
        f'<span class="tw-nav__brand">{esc(p.identity.name)}</span>'
        f'<div class="tw-nav__links">{"".join(links)}</div>'
        "</div></nav>"
    )


def render_hero(p: Profile) -> str:
    identity = p.identity

    if identity.photo:
        portrait = (
            f'<img class="tw-hero__photo" src="{esc(identity.photo)}" '
            f'alt="{esc(identity.name)}" />'
        )
    else:
        portrait = (
            f'<div class="tw-hero__photo tw-hero__initials">'
            f"{esc(_initials(identity.name))}</div>"
        )

    eyebrow_text = identity.location or "Portfolio"
    tagline = (
        f'<p class="tw-hero__tagline">{esc(identity.tagline)}</p>' if identity.tagline else ""
    )

    return (
        '<header class="tw-hero"><div class="tw-hero__glow"></div>'
        '<div class="tw-hero__text">'
        f'<span class="tw-hero__eyebrow">{esc(eyebrow_text)}</span>'
        f'<h1 class="tw-hero__name">{esc(identity.name)}</h1>'
        f'<p class="tw-hero__role">{esc(identity.role)}</p>'
        f"{tagline}"
        "</div>"
        f"{portrait}"
        "</header>"
    )


def render_about(p: Profile) -> str:
    if not p.about:
        return ""
    paragraphs = "".join(f"<p>{esc(text)}</p>" for text in p.about)
    return (
        '<section class="tw-section" id="about">'
        f"{_eyebrow('About')}"
        '<h2 class="tw-section__title">Who I am</h2>'
        f'<div class="tw-card tw-prose">{paragraphs}</div>'
        "</section>"
    )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_sections.py -v`
Expected: 17 passed (the two `safe_href` tests are parametrized three ways each).

- [ ] **Step 5: Commit**

```bash
git add sections.py tests/test_sections.py
git commit -m "feat: add nav, hero and about section renderers"
```

---

## Task 4: Section renderers — journey, portfolio, contact, footer

**Files:**
- Modify: `sections.py`
- Modify: `tests/test_sections.py`

**Interfaces:**
- Consumes: `esc`, `safe_href`, `_eyebrow` from Task 3.
- Produces (Task 5 styles these, Task 7 calls them):
  - `render_journey(p: Profile) -> str`
  - `render_portfolio(p: Profile) -> str`
  - `render_contact(p: Profile) -> str`
  - `render_footer(p: Profile) -> str`
  - **CSS class contract:** `tw-timeline`, `tw-timeline__item`, `tw-timeline__period`,
    `tw-timeline__role`, `tw-timeline__org`, `tw-timeline__detail`,
    `tw-tags`, `tw-tag`, `tw-grid`, `tw-project`, `tw-project__title`,
    `tw-project__blurb`, `tw-project__link`, `tw-contact`, `tw-contact__intro`,
    `tw-contact__links`, `tw-contact__link`, `tw-footer`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_sections.py`:

```python
from profile import JourneyEntry, PortfolioEntry
from sections import render_contact, render_footer, render_journey, render_portfolio


def test_journey_renders_one_item_per_entry():
    p = make_profile(
        journey=[
            JourneyEntry(period="2025 —", role="Engineer", org="Entirely"),
            JourneyEntry(period="2021 — 2025", role="Dev", org="censhare"),
        ]
    )
    html = render_journey(p)
    assert html.count("tw-timeline__item") == 2
    assert 'id="journey"' in html


def test_journey_renders_tags_and_optional_detail():
    p = make_profile(
        journey=[
            JourneyEntry(period="2025 —", role="Engineer", org="Entirely",
                         detail="R&D.", tags=["Java", "Kafka"])
        ]
    )
    html = render_journey(p)
    assert html.count('class="tw-tag"') == 2
    assert "R&amp;D." in html


def test_journey_omits_detail_block_when_absent():
    p = make_profile(journey=[JourneyEntry(period="2025 —", role="Eng", org="X")])
    assert "tw-timeline__detail" not in render_journey(p)


def test_journey_is_empty_when_unconfigured():
    assert render_journey(make_profile()) == ""


def test_portfolio_renders_one_card_per_entry():
    p = make_profile(
        portfolio=[
            PortfolioEntry(title="A", blurb="one"),
            PortfolioEntry(title="B", blurb="two"),
        ]
    )
    html = render_portfolio(p)
    assert html.count("tw-project__title") == 2
    assert 'id="portfolio"' in html


def test_portfolio_links_only_when_a_url_is_given():
    with_url = make_profile(portfolio=[PortfolioEntry(title="A", blurb="x", url="https://a.dev")])
    without = make_profile(portfolio=[PortfolioEntry(title="A", blurb="x")])
    assert "tw-project__link" in render_portfolio(with_url)
    assert "tw-project__link" not in render_portfolio(without)


def test_portfolio_rejects_an_executable_url():
    p = make_profile(portfolio=[PortfolioEntry(title="A", blurb="x", url="javascript:alert(1)")])
    with pytest.raises(ValueError):
        render_portfolio(p)


def test_portfolio_is_empty_when_unconfigured():
    assert render_portfolio(make_profile()) == ""


def test_contact_renders_intro_and_links():
    p = make_profile(
        contact=Contact(
            intro="Say hi.",
            links=[ContactLink(label="Email", href="mailto:a@b.dev")],
        )
    )
    html = render_contact(p)
    assert "Say hi." in html
    assert 'href="mailto:a@b.dev"' in html
    assert 'id="contact"' in html


def test_contact_is_empty_without_links():
    assert render_contact(make_profile()) == ""
    assert render_contact(make_profile(contact=Contact(intro="Hi"))) == ""


def test_contact_rejects_an_executable_href():
    p = make_profile(contact=Contact(links=[ContactLink(label="x", href="javascript:alert(1)")]))
    with pytest.raises(ValueError):
        render_contact(p)


def test_footer_names_the_person():
    assert "Ada Lovelace" in render_footer(make_profile())
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_sections.py -v`
Expected: FAIL — `ImportError: cannot import name 'render_journey' from 'sections'`

- [ ] **Step 3: Write the implementation**

Append to `sections.py`:

```python
def _tags(tags: list[str]) -> str:
    if not tags:
        return ""
    chips = "".join(f'<span class="tw-tag">{esc(tag)}</span>' for tag in tags)
    return f'<div class="tw-tags">{chips}</div>'


def render_journey(p: Profile) -> str:
    if not p.journey:
        return ""

    items = []
    for entry in p.journey:
        where = f"{entry.org} · {entry.location}" if entry.location else entry.org
        detail = (
            f'<p class="tw-timeline__detail">{esc(entry.detail)}</p>' if entry.detail else ""
        )
        items.append(
            '<li class="tw-timeline__item">'
            f'<span class="tw-timeline__period">{esc(entry.period)}</span>'
            f'<h3 class="tw-timeline__role">{esc(entry.role)}</h3>'
            f'<p class="tw-timeline__org">{esc(where)}</p>'
            f"{detail}"
            f"{_tags(entry.tags)}"
            "</li>"
        )

    return (
        '<section class="tw-section" id="journey">'
        f"{_eyebrow('Journey')}"
        '<h2 class="tw-section__title">Where I have worked</h2>'
        f'<ol class="tw-timeline">{"".join(items)}</ol>'
        "</section>"
    )


def render_portfolio(p: Profile) -> str:
    if not p.portfolio:
        return ""

    cards = []
    for entry in p.portfolio:
        link = (
            f'<a class="tw-project__link" href="{safe_href(entry.url)}" '
            'target="_blank" rel="noopener noreferrer">View →</a>'
            if entry.url
            else ""
        )
        cards.append(
            '<article class="tw-card tw-project">'
            f'<h3 class="tw-project__title">{esc(entry.title)}</h3>'
            f'<p class="tw-project__blurb">{esc(entry.blurb)}</p>'
            f"{_tags(entry.tags)}"
            f"{link}"
            "</article>"
        )

    return (
        '<section class="tw-section" id="portfolio">'
        f"{_eyebrow('Portfolio')}"
        '<h2 class="tw-section__title">Selected work</h2>'
        f'<div class="tw-grid">{"".join(cards)}</div>'
        "</section>"
    )


def render_contact(p: Profile) -> str:
    if not p.contact or not p.contact.links:
        return ""

    intro = (
        f'<p class="tw-contact__intro">{esc(p.contact.intro)}</p>' if p.contact.intro else ""
    )
    links = "".join(
        f'<a class="tw-contact__link" href="{safe_href(link.href)}">{esc(link.label)}</a>'
        for link in p.contact.links
    )
    return (
        '<section class="tw-section tw-contact" id="contact">'
        f"{_eyebrow('Contact')}"
        '<h2 class="tw-section__title">Get in touch</h2>'
        f'<div class="tw-card">{intro}<div class="tw-contact__links">{links}</div></div>'
        "</section>"
    )


def render_footer(p: Profile) -> str:
    return f'<footer class="tw-footer">{esc(p.identity.name)} · built with Gradio</footer>'
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_sections.py -v`
Expected: 29 passed.

- [ ] **Step 5: Commit**

```bash
git add sections.py tests/test_sections.py
git commit -m "feat: add journey, portfolio, contact and footer renderers"
```

---

## Task 5: Theme — palette-driven CSS

**Files:**
- Create: `theme.py`
- Create: `tests/test_theme.py`
- Delete: `styles.py`

**Interfaces:**
- Consumes: `Theme` from Task 1; the CSS class contract from Tasks 3–4.
- Produces: `build_css(theme: Theme) -> str`, `JS: str` — both used by `app.py` in Task 7.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_theme.py`:

```python
import re

from profile import Theme
from theme import CSS_TEMPLATE, JS, build_css


def test_every_theme_token_reaches_the_root_block():
    css = build_css(Theme())
    for field, value in Theme().model_dump().items():
        assert f"--tw-{field.replace('_', '-')}: {value}" in css


def test_overridden_token_is_used():
    css = build_css(Theme(accent="#FF0000"))
    assert "--tw-accent: #FF0000" in css
    assert "--tw-accent: #F0B429" not in css


def test_template_body_contains_no_palette_literals():
    """Colours live in the config, not in the stylesheet."""
    palette = {v.lower() for v in Theme().model_dump().values()}
    found = {m.lower() for m in re.findall(r"#[0-9a-fA-F]{6}", CSS_TEMPLATE)}
    assert not (found & palette), f"hardcoded palette colours in template: {found & palette}"


def test_css_styles_the_documented_class_contract():
    css = build_css(Theme())
    for cls in [
        "tw-nav", "tw-nav__link", "tw-hero", "tw-hero__name", "tw-hero__photo",
        "tw-hero__initials", "tw-section", "tw-section__eyebrow", "tw-section__title",
        "tw-card", "tw-prose", "tw-timeline", "tw-timeline__item", "tw-timeline__period",
        "tw-tags", "tw-tag", "tw-grid", "tw-project", "tw-project__link",
        "tw-contact__links", "tw-contact__link", "tw-footer",
    ]:
        assert f".{cls}" in css, f"missing style for .{cls}"


def test_chat_panel_is_pinned():
    css = build_css(Theme())
    assert "#twin-panel" in css
    assert "position: fixed" in css


def test_js_is_a_javascript_arrow_function():
    assert JS.strip().startswith("()")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_theme.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'theme'`

- [ ] **Step 3: Write the implementation**

Create `theme.py`:

```python
"""Build the stylesheet from the configured palette.

`CSS_TEMPLATE` references `--tw-*` custom properties only — no colour literals.
`build_css` emits the `:root` block from the Theme model and prepends it, so
every colour on the page traces back to profile.yaml.
"""

from __future__ import annotations

from profile import Theme

CSS_TEMPLATE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ---------- Reset the Gradio chrome we do not want ---------- */
footer, .built-with, .show-api, .api-docs { display: none !important; }

html, body, gradio-app {
  background: var(--tw-bg) !important;
  color: var(--tw-text);
}

body {
  background-image: radial-gradient(var(--tw-grid) 1px, transparent 1px) !important;
  background-size: 26px 26px !important;
}

.gradio-container {
  background: transparent !important;
  color: var(--tw-text) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  max-width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
}
.gradio-container .block, .gradio-container .form {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
}

/* ---------- Page rhythm ---------- */
.tw-nav, .tw-hero, .tw-section, .tw-footer {
  max-width: 940px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 24px;
  padding-right: 24px;
  box-sizing: border-box;
}

/* ---------- Nav ---------- */
.tw-nav {
  position: sticky;
  top: 0;
  z-index: 40;
  max-width: 100%;
  backdrop-filter: blur(14px);
  background: color-mix(in srgb, var(--tw-bg) 78%, transparent);
  border-bottom: 1px solid var(--tw-border);
}
.tw-nav__inner {
  max-width: 940px;
  margin: 0 auto;
  padding: 14px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.tw-nav__brand {
  font-weight: 600;
  font-size: 14px;
  letter-spacing: -0.01em;
}
.tw-nav__links { display: flex; gap: 22px; flex-wrap: wrap; }
.tw-nav__link {
  color: var(--tw-muted);
  text-decoration: none;
  font-size: 13.5px;
  transition: color 0.15s ease;
}
.tw-nav__link:hover { color: var(--tw-text); }
.tw-nav__link--cta { color: var(--tw-accent); }
.tw-nav__link--cta:hover { color: var(--tw-accent-alt); }

/* ---------- Hero ---------- */
.tw-hero {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 44px;
  padding-top: 92px;
  padding-bottom: 72px;
}
.tw-hero__glow {
  position: absolute;
  top: -140px;
  right: -80px;
  width: 520px;
  height: 520px;
  pointer-events: none;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--tw-accent) 22%, transparent) 0%,
    transparent 68%
  );
  filter: blur(30px);
}
.tw-hero__text { position: relative; max-width: 560px; }
.tw-hero__eyebrow {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--tw-accent);
  border: 1px solid var(--tw-border);
  border-radius: 999px;
  padding: 5px 12px;
  margin-bottom: 22px;
}
.tw-hero__name {
  font-size: clamp(38px, 6vw, 62px);
  font-weight: 700;
  line-height: 1.04;
  letter-spacing: -0.035em;
  margin: 0 0 10px;
  background: linear-gradient(100deg, var(--tw-accent) 8%, var(--tw-accent-alt) 82%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.tw-hero__role {
  font-size: 17px;
  font-weight: 500;
  color: var(--tw-text);
  margin: 0 0 16px;
}
.tw-hero__tagline {
  font-size: 15.5px;
  line-height: 1.72;
  color: var(--tw-muted);
  margin: 0;
}
.tw-hero__photo {
  position: relative;
  flex: 0 0 auto;
  width: 172px;
  height: 172px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--tw-border);
  box-shadow:
    0 0 0 6px color-mix(in srgb, var(--tw-surface) 60%, transparent),
    0 26px 60px -22px color-mix(in srgb, var(--tw-accent) 45%, transparent);
}
.tw-hero__initials {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 46px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: var(--tw-muted);
  background: var(--tw-surface);
}

/* ---------- Sections ---------- */
.tw-section { padding-top: 26px; padding-bottom: 46px; scroll-margin-top: 76px; }
.tw-section__eyebrow {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--tw-muted);
  margin-bottom: 10px;
}
.tw-section__title {
  font-size: 27px;
  font-weight: 650;
  letter-spacing: -0.02em;
  margin: 0 0 24px;
  color: var(--tw-text);
}
.tw-card {
  background: var(--tw-surface);
  border: 1px solid var(--tw-border);
  border-radius: 14px;
  padding: 26px 28px;
}
.tw-prose p {
  font-size: 15px;
  line-height: 1.78;
  color: var(--tw-muted);
  margin: 0 0 15px;
}
.tw-prose p:last-child { margin-bottom: 0; }

/* ---------- Journey timeline ---------- */
.tw-timeline {
  list-style: none;
  margin: 0;
  padding: 0 0 0 26px;
  border-left: 1px solid var(--tw-border);
}
.tw-timeline__item { position: relative; padding: 0 0 34px 0; }
.tw-timeline__item:last-child { padding-bottom: 0; }
.tw-timeline__item::before {
  content: "";
  position: absolute;
  left: -32px;
  top: 5px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--tw-bg);
  border: 2px solid var(--tw-accent);
}
.tw-timeline__period {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11.5px;
  letter-spacing: 0.06em;
  color: var(--tw-muted);
}
.tw-timeline__role {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 6px 0 3px;
  color: var(--tw-text);
}
.tw-timeline__org {
  font-size: 13.5px;
  color: var(--tw-accent);
  margin: 0 0 10px;
}
.tw-timeline__detail {
  font-size: 14.5px;
  line-height: 1.72;
  color: var(--tw-muted);
  margin: 0 0 12px;
  max-width: 640px;
}

/* ---------- Tags ---------- */
.tw-tags { display: flex; flex-wrap: wrap; gap: 7px; }
.tw-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.04em;
  color: var(--tw-muted);
  background: var(--tw-surface-alt);
  border: 1px solid var(--tw-border);
  border-radius: 999px;
  padding: 4px 10px;
}

/* ---------- Portfolio ---------- */
.tw-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
}
.tw-project {
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: border-color 0.18s ease, transform 0.18s ease;
}
.tw-project:hover {
  border-color: color-mix(in srgb, var(--tw-accent) 55%, var(--tw-border));
  transform: translateY(-2px);
}
.tw-project__title {
  font-size: 16.5px;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 0;
  color: var(--tw-text);
}
.tw-project__blurb {
  font-size: 14px;
  line-height: 1.7;
  color: var(--tw-muted);
  margin: 0;
  flex: 1;
}
.tw-project__link {
  align-self: flex-start;
  font-size: 13px;
  font-weight: 500;
  color: var(--tw-accent);
  text-decoration: none;
}
.tw-project__link:hover { color: var(--tw-accent-alt); }

/* ---------- Contact ---------- */
.tw-contact__intro {
  font-size: 15px;
  line-height: 1.74;
  color: var(--tw-muted);
  margin: 0 0 20px;
}
.tw-contact__links { display: flex; flex-wrap: wrap; gap: 10px; }
.tw-contact__link {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--tw-text);
  text-decoration: none;
  border: 1px solid var(--tw-border);
  border-radius: 10px;
  padding: 10px 18px;
  transition: border-color 0.18s ease, color 0.18s ease;
}
.tw-contact__link:hover {
  color: var(--tw-accent);
  border-color: color-mix(in srgb, var(--tw-accent) 55%, var(--tw-border));
}

/* ---------- Footer ---------- */
.tw-footer {
  padding-top: 40px;
  padding-bottom: 120px;
  font-size: 12.5px;
  color: var(--tw-muted);
  text-align: center;
}

/* ---------- Pinned twin panel ---------- */
#twin-panel {
  position: fixed !important;
  right: 22px;
  bottom: 22px;
  z-index: 60;
  width: 380px;
  max-height: 72vh;
  gap: 0 !important;
  background: var(--tw-surface) !important;
  border: 1px solid var(--tw-border) !important;
  border-radius: 16px !important;
  overflow: hidden;
  box-shadow: 0 30px 70px -24px rgba(0, 0, 0, 0.72);
}
#twin-panel.tw-collapsed .tw-panel__body { display: none; }
#twin-panel.tw-collapsed { max-height: none; }

.tw-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--tw-border);
  cursor: pointer;
}
#twin-panel.tw-collapsed .tw-panel__head { border-bottom: 0; }
.tw-panel__title { font-size: 14px; font-weight: 600; margin: 0; }
.tw-panel__sub { font-size: 12px; color: var(--tw-muted); margin: 2px 0 0; }
.tw-panel__toggle {
  color: var(--tw-muted);
  font-size: 16px;
  line-height: 1;
  background: none;
  border: 0;
  cursor: pointer;
}

#twin-panel .chatbot, #twin-panel .chatbot.block {
  background: transparent !important;
  border: 0 !important;
  min-height: 240px !important;
  max-height: 42vh !important;
  box-shadow: none !important;
}
#twin-panel .message-row,
#twin-panel .message-row > div,
#twin-panel .message-wrap,
#twin-panel .bubble-wrap {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}
#twin-panel .message,
#twin-panel .message-bubble,
#twin-panel .bubble {
  background: var(--tw-surface-alt) !important;
  color: var(--tw-text) !important;
  border: 1px solid var(--tw-border) !important;
  border-radius: 12px !important;
  font-size: 13.5px !important;
  line-height: 1.62 !important;
  padding: 10px 13px !important;
}
#twin-panel .message p, #twin-panel .prose p {
  font-size: 13.5px !important;
  line-height: 1.62 !important;
  color: inherit !important;
  margin: 0 0 7px !important;
}
#twin-panel .message p:last-child, #twin-panel .prose p:last-child {
  margin-bottom: 0 !important;
}
#twin-panel .message a { color: var(--tw-accent) !important; }

.tw-examples { display: flex; flex-direction: column; gap: 6px; padding: 0 12px 8px; }
.tw-examples button {
  text-align: left !important;
  font-size: 12.5px !important;
  color: var(--tw-muted) !important;
  background: var(--tw-surface-alt) !important;
  border: 1px solid var(--tw-border) !important;
  border-radius: 10px !important;
  padding: 9px 12px !important;
  min-height: 0 !important;
  transition: color 0.15s ease, border-color 0.15s ease;
}
.tw-examples button:hover {
  color: var(--tw-text) !important;
  border-color: color-mix(in srgb, var(--tw-accent) 55%, var(--tw-border)) !important;
}

.tw-composer { padding: 10px 12px 12px; gap: 8px !important; }
#twin-panel textarea, #twin-panel input[type="text"] {
  background: var(--tw-bg) !important;
  border: 1px solid var(--tw-border) !important;
  border-radius: 10px !important;
  color: var(--tw-text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13.5px !important;
  padding: 10px 12px !important;
  min-height: 42px !important;
}
#twin-panel textarea:focus {
  outline: none !important;
  border-color: color-mix(in srgb, var(--tw-accent) 60%, var(--tw-border)) !important;
  box-shadow: none !important;
}
#twin-panel textarea::placeholder { color: var(--tw-muted) !important; }

#twin-panel button.primary, #twin-panel .tw-send button, #twin-panel .tw-send {
  background: var(--tw-accent) !important;
  border: 1px solid var(--tw-accent) !important;
  border-radius: 10px !important;
  color: var(--tw-bg) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  min-height: 42px !important;
}
#twin-panel button.primary:hover, #twin-panel .tw-send:hover {
  background: var(--tw-accent-alt) !important;
  border-color: var(--tw-accent-alt) !important;
}

/* ---------- Scrollbar + selection ---------- */
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--tw-border); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--tw-muted); }
::selection { background: var(--tw-accent); color: var(--tw-bg); }

@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
  .tw-project:hover { transform: none; }
}

@media (max-width: 780px) {
  .tw-hero { flex-direction: column-reverse; align-items: flex-start; gap: 28px; padding-top: 56px; }
  .tw-hero__photo { width: 116px; height: 116px; }
  .tw-nav__links { gap: 14px; }
  #twin-panel {
    right: 0;
    left: 0;
    bottom: 0;
    width: auto;
    border-radius: 16px 16px 0 0;
    max-height: 78vh;
  }
  .tw-footer { padding-bottom: 180px; }
}
"""


def build_css(theme: Theme) -> str:
    """Render the palette into a :root block and prepend it to the template."""
    lines = [
        f"  --tw-{field.replace('_', '-')}: {value};"
        for field, value in theme.model_dump().items()
    ]
    lines.append("  --tw-grid: color-mix(in srgb, var(--tw-accent) 5%, transparent);")
    root = ":root {\n" + "\n".join(lines) + "\n}\n"
    return root + CSS_TEMPLATE


JS = """
() => {
  const panel = document.getElementById('twin-panel');
  if (!panel) return;

  const head = panel.querySelector('.tw-panel__head');
  if (head && !head.dataset.twBound) {
    head.dataset.twBound = '1';
    head.addEventListener('click', () => panel.classList.toggle('tw-collapsed'));
  }

  const opener = document.getElementById('twin-panel-open');
  if (opener && !opener.dataset.twBound) {
    opener.dataset.twBound = '1';
    opener.addEventListener('click', (e) => {
      e.preventDefault();
      panel.classList.remove('tw-collapsed');
      const box = panel.querySelector('textarea');
      if (box) box.focus();
    });
  }
}
"""
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_theme.py -v`
Expected: 6 passed.

- [ ] **Step 5: Delete the old stylesheet module**

```bash
git rm styles.py
```

Note: `app.py` still imports it and is now broken. Task 7 fixes it. Do not run `app.py` until then.

- [ ] **Step 6: Commit**

```bash
git add theme.py tests/test_theme.py
git commit -m "refactor: replace styles.py with palette-driven theme.py"
```

---

## Task 6: Prompt context from configured sources

**Files:**
- Rewrite: `context.py`
- Create: `tests/test_context.py`

**Interfaces:**
- Consumes: `Profile`, `Source` from Task 1.
- Produces: `build_system_prompt(profile: Profile, base_dir: Path | None = None) -> str` — used by `app.py` in Task 7. The old module-level `TWIN_SYSTEM_PROMPT` constant is **removed**.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_context.py`:

```python
import pytest

from context import build_system_prompt
from profile import Identity, Profile, Source, TwinConfig


def make(tmp_path, sources) -> Profile:
    return Profile(
        identity=Identity(name="Ada Lovelace", role="Engineer"),
        twin=TwinConfig(sources=sources),
    )


def test_prompt_names_the_person(tmp_path):
    prompt = build_system_prompt(make(tmp_path, []), base_dir=tmp_path)
    assert "Ada Lovelace" in prompt


def test_prompt_keeps_the_behavioural_rules(tmp_path):
    prompt = build_system_prompt(make(tmp_path, []), base_dir=tmp_path)
    assert "record" in prompt.lower()
    assert "never make up an answer" in prompt.lower()


def test_text_source_is_included(tmp_path):
    (tmp_path / "bio.txt").write_text("Loves Kebap.", encoding="utf-8")
    profile = make(tmp_path, [Source(type="text", path="bio.txt")])
    assert "Loves Kebap." in build_system_prompt(profile, base_dir=tmp_path)


def test_sources_appear_in_config_order(tmp_path):
    (tmp_path / "a.txt").write_text("FIRST_MARKER", encoding="utf-8")
    (tmp_path / "b.txt").write_text("SECOND_MARKER", encoding="utf-8")
    profile = make(
        tmp_path,
        [Source(type="text", path="a.txt"), Source(type="text", path="b.txt")],
    )
    prompt = build_system_prompt(profile, base_dir=tmp_path)
    assert prompt.index("FIRST_MARKER") < prompt.index("SECOND_MARKER")


def test_missing_source_names_index_and_path(tmp_path):
    profile = make(tmp_path, [Source(type="text", path="gone.txt")])
    with pytest.raises(FileNotFoundError) as exc:
        build_system_prompt(profile, base_dir=tmp_path)
    assert "gone.txt" in str(exc.value)
    assert "sources[0]" in str(exc.value)


def test_pdf_source_is_extracted(tmp_path):
    from pathlib import Path

    repo = Path(__file__).resolve().parent.parent
    profile = make(tmp_path, [Source(type="pdf", path="linkedin.pdf")])
    prompt = build_system_prompt(profile, base_dir=repo)
    assert "Mithat Konuk" in prompt
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_context.py -v`
Expected: FAIL — `ImportError: cannot import name 'build_system_prompt' from 'context'`

- [ ] **Step 3: Write the implementation**

Replace the entire contents of `context.py`:

```python
"""Build the twin's system prompt from the sources listed in profile.yaml.

Which files feed the prompt is configuration, not code: add a `sources:` entry
and it is picked up. Loading is dispatched on the declared type so a new format
means one new loader, not edits scattered through this module.
"""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from profile import Profile, Source

BASE_DIR = Path(__file__).parent


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "".join(page.extract_text() or "" for page in reader.pages)


LOADERS = {"text": _load_text, "pdf": _load_pdf}


def _load_source(source: Source, index: int, base_dir: Path) -> str:
    loader = LOADERS.get(source.type)
    if loader is None:
        supported = ", ".join(sorted(LOADERS))
        raise ValueError(
            f"Unsupported source type {source.type!r} at twin.sources[{index}]. "
            f"Supported types: {supported}"
        )

    path = base_dir / source.path
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt source not found for twin.sources[{index}]: {path}"
        )
    return loader(path)


def build_system_prompt(profile: Profile, base_dir: Path | None = None) -> str:
    """Assemble the system prompt for the person described by `profile`."""
    root = base_dir or BASE_DIR
    name = profile.identity.name

    blocks = [
        _load_source(source, index, root)
        for index, source in enumerate(profile.twin.sources)
    ]
    context = "\n\n".join(block.strip() for block in blocks if block.strip())

    return f"""
# Your role

You are the digital twin of {name}, running on their personal website and
chatting with its visitors. You represent {name}.
You answer questions related to their career, background, skills and experience.

If asked, you explain clearly that you are an AI that is the digital twin of {name}.

# Context

Here is everything you know about {name}:

{context}

# Rules

Engage with the user. Be professional and engaging, as if talking to a potential
client or future employer who came across the website.
Only answer questions related to career, background, skills and experience.
If the user asks about something unrelated, steer the conversation back to
professional topics.

Always stay in character as the digital twin of {name}.

If the user would like to get in touch, ask for their email and use your tool to
record it for follow-up.

IMPORTANT:
If you don't know the answer, use your tool to record the question, then tell the
user that you don't know. Never make up an answer.

Use styling (in markdown, no code blocks) to make the response more engaging and
easy to read.
""".strip()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_context.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add context.py tests/test_context.py
git commit -m "feat: build system prompt from configured sources"
```

---

## Task 7: Gradio assembly and chat wiring

**Files:**
- Rewrite: `app.py`

**Interfaces:**
- Consumes: `load_profile` (T1), all `render_*` (T3, T4), `build_css`/`JS` (T5), `build_system_prompt` (T6), and the untouched `tools`/`handle_tool_calls`.
- Produces: a runnable `python app.py`.

**Why hand-wired:** `gr.ChatInterface` renders its own full-page layout and cannot be nested inside a custom `gr.Blocks` arrangement, so the submit / clear / example-click glue it provided is rebuilt here. This is the only non-mechanical part of the plan.

- [ ] **Step 1: Replace app.py**

```python
"""Entry point: assemble the profile page and wire the twin's chat panel."""

import os

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from context import build_system_prompt
from profile import load_profile
from sections import (
    render_about,
    render_contact,
    render_footer,
    render_hero,
    render_journey,
    render_nav,
    render_portfolio,
)
from theme import JS, build_css
from tools import handle_tool_calls, tools

load_dotenv(override=True)

profile = load_profile()
system = [{"role": "system", "content": build_system_prompt(profile)}]

openai = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def chat(message, history):
    """Run one turn, resolving any tool calls the model requests."""
    messages = system + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(
        model=profile.twin.model, messages=messages, tools=tools
    )
    while response.choices[0].finish_reason == "tool_calls":
        reply = response.choices[0].message
        results = handle_tool_calls(reply.tool_calls)
        messages.append(reply)
        messages.extend(results)
        response = openai.chat.completions.create(
            model=profile.twin.model, messages=messages, tools=tools
        )
    return response.choices[0].message.content


def respond(message, history):
    """Chat callback: append the turn, clear the box. Errors surface in-panel."""
    message = (message or "").strip()
    if not message:
        return history, ""

    try:
        reply = chat(message, history)
    except Exception as e:  # noqa: BLE001 - surface any failure to the visitor
        reply = f"Sorry — I couldn't reach the model just now. ({type(e).__name__})"
        print(f"chat failed: {e!r}", flush=True)

    return (
        history
        + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ],
        "",
    )


def panel_header() -> str:
    sub = (
        f'<p class="tw-panel__sub">{profile.twin.subheading}</p>'
        if profile.twin.subheading
        else ""
    )
    return (
        '<div class="tw-panel__head">'
        f'<div><p class="tw-panel__title">{profile.twin.heading}</p>{sub}</div>'
        '<button class="tw-panel__toggle" type="button">—</button>'
        "</div>"
    )


with gr.Blocks(title=f"{profile.identity.name} · {profile.identity.role}") as demo:
    gr.HTML(render_nav(profile))
    gr.HTML(render_hero(profile))
    gr.HTML(render_about(profile))
    gr.HTML(render_journey(profile))
    gr.HTML(render_portfolio(profile))
    gr.HTML(render_contact(profile))
    gr.HTML(render_footer(profile))

    with gr.Column(elem_id="twin-panel"):
        gr.HTML(panel_header())
        with gr.Column(elem_classes="tw-panel__body"):
            chatbot = gr.Chatbot(
                value=(
                    [{"role": "assistant", "content": profile.twin.greeting}]
                    if profile.twin.greeting
                    else []
                ),
                show_label=False,
                container=False,
            )
            with gr.Column(elem_classes="tw-examples"):
                example_buttons = [
                    gr.Button(text, size="sm") for text in profile.twin.examples
                ]
            with gr.Row(elem_classes="tw-composer"):
                msg = gr.Textbox(
                    placeholder="Ask about experience, skills, background…",
                    show_label=False,
                    container=False,
                    lines=1,
                    scale=5,
                )
                send = gr.Button("Send", variant="primary", scale=1, elem_classes="tw-send")

    msg.submit(respond, [msg, chatbot], [chatbot, msg])
    send.click(respond, [msg, chatbot], [chatbot, msg])

    for button, text in zip(example_buttons, profile.twin.examples):
        button.click(lambda t=text: t, None, msg).then(
            respond, [msg, chatbot], [chatbot, msg]
        )


if __name__ == "__main__":
    demo.launch(css=build_css(profile.theme), js=JS, theme=gr.themes.Base())
```

- [ ] **Step 2: Verify the module imports and the full suite passes**

Run: `.venv/bin/python -c "import app; print('ok', app.profile.identity.name)"`
Expected: `ok Mithat Konuk`

Run: `.venv/bin/python -m pytest tests/ -v`
Expected: all tests pass (51 total — 10 profile, 29 sections, 6 theme, 6 context).

- [ ] **Step 3: Launch and inspect**

Run: `.venv/bin/python app.py`

Open the printed URL and check, in order:

1. The nav, hero, About, Journey, Portfolio, Contact and footer all render as HTML — not as escaped text on screen.
2. The twin panel is pinned bottom-right and expanded.
3. Clicking the panel header collapses and re-expands it; the nav's "Digital Twin" link re-opens it and focuses the box.
4. Typing a message produces a reply and clears the input.
5. Clicking an example prompt fills the box and sends it.
6. Narrow the window below 780px: the panel becomes a bottom sheet, the hero stacks.

**If section HTML appears escaped or Gradio's own styles override the layout**, pass `apply_default_css=False` to each `gr.HTML(...)` call — this is a Gradio 6 option that suppresses its default component styling. Re-check.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: assemble profile page with pinned twin chat panel"
```

---

## Task 8: Documentation and screenshot

**Files:**
- Modify: `README.md`
- Replace: `assets/screenshot.png`

- [ ] **Step 1: Capture a new screenshot**

With `app.py` running, take a full-page screenshot of the site and save it over `assets/screenshot.png`.

- [ ] **Step 2: Rewrite the README**

Update these sections to match reality:

- **Intro** — it is a personal site with an AI twin panel, not only a chatbot.
- **How it works** — `profile.yaml` is the single source of content and colour; `profile.py` validates it; `sections.py` / `theme.py` / `context.py` consume it; `app.py` assembles the Gradio page.
- **Project layout** — replace the file table with:

```
profile.yaml     # All content + palette. Edit this to make the site yours.
profile.py       # Pydantic schema + validating loader for profile.yaml
sections.py      # Pure Profile -> HTML renderers, one per page section
theme.py         # Builds the stylesheet from the configured palette; page JS
context.py       # Builds the twin's system prompt from twin.sources
app.py           # Gradio assembly + chat wiring (only module importing gradio)
tools.py         # Tool implementations (record_user_details, record_unknown_question)
tool_loader.py   # Loads + validates tools.json into OpenAI-style tool schemas
tools.json       # Tool (function-calling) schema definitions
summary.txt      # Short bio, referenced from twin.sources
linkedin.pdf     # LinkedIn export, referenced from twin.sources
tests/           # pytest suite
```

- **Setup** — step 3 becomes "Edit `profile.yaml`", noting `twin.model` lives there now rather than in `app.py`, and that `summary.txt`/`linkedin.pdf` are referenced from `twin.sources`.
- **Customizing** — collapse to: content, colours, sections, chat examples and model are all `profile.yaml`; tools are `tools.json` + `tools.py`; layout markup is `sections.py`, CSS is `theme.py`.
- **Testing** — new short section: `.venv/bin/python -m pytest tests/ -v`.

- [ ] **Step 3: Verify links**

Run: `.venv/bin/python -c "
import re, pathlib
md = pathlib.Path('README.md').read_text()
missing = [t for t in re.findall(r'\]\(([^)h][^)]*)\)', md) if not pathlib.Path(t.split('#')[0]).exists()]
print('broken:', missing)
"`
Expected: `broken: []`

- [ ] **Step 4: Commit**

```bash
git add README.md assets/screenshot.png
git commit -m "docs: describe the config-driven site"
```

---

## Self-review notes

Checked against the spec:

- Config schema, loader, error philosophy → Task 1
- Content seeding from `linkedin.pdf` → Task 2
- `sections.py` purity, escaping, href allowlist, empty-section omission → Tasks 3, 4
- `theme.py` palette injection, dropped terminal styling, dark-only palette → Task 5
- `context.py` source dispatch and prompt template → Task 6
- `app.py` Blocks layout, hand-wired chat, pinned panel, `MODEL_NAME` from config → Task 7
- `styles.py` deletion, README rewrite, screenshot → Tasks 5, 8
- Error-handling table rows each have a covering test except "Pushover env unset" (unchanged behaviour, out of scope) and "photo file missing on disk" (the browser's own broken-image behaviour; the `photo` *unset* case is tested)

Type consistency: `Profile` field names used in Tasks 3–7 match the models defined in Task 1; the `tw-` class contract declared in Tasks 3–4 matches the selectors asserted in Task 5's `test_css_styles_the_documented_class_contract`.
