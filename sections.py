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
