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
    assert "line" in str(exc.value)
