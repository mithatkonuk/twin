"""Load and validate the site profile — the single source of content and colour.

Everything the page shows and every colour it uses comes from `profile.yaml`.
Swapping that file swaps the whole site. Validation happens on the first call to
load_profile(), with results cached thereafter, so a typo surfaces early with the
field named rather than as a confusing failure deep inside a render or an API call.
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
    """Palette tokens. Every field has a default, so `theme:` may be omitted.

    The default is a light, frosted-glass palette: a cool grey-blue page, white
    glass cards, navy ink and a slate-blue accent that also drives the deep
    gradient band. `highlight` is the glass tint and the text colour on that band.
    """

    bg: str = "#E8EDF3"
    surface: str = "#F7F9FC"
    surface_alt: str = "#EEF2F7"
    border: str = "#D9E0EA"
    text: str = "#1A2238"
    muted: str = "#6E7890"
    accent: str = "#3C5A8A"
    accent_alt: str = "#8EA3C4"
    highlight: str = "#FFFFFF"


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
