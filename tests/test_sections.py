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
