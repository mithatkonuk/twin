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
