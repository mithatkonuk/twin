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
