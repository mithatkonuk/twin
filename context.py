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
