"""Entry point: assemble the profile page and wire the twin's chat panel."""

import os
from pathlib import Path

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

# `identity.photo` in profile.yaml points at "/gradio_api/file=assets/photo.jpg"
# — the route Gradio 6 serves static files from. Gradio only serves paths it has
# been told are safe, so register the assets directory (straight from disk, no
# upload-cache copy).
gr.set_static_paths(paths=[Path(__file__).resolve().parent / "assets"])

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
    """Chat callback: append the turn, clear the box. Errors surface in-panel.

    Third output hides the starter questions: they are a prompt for a visitor
    who has not asked anything yet, so once the conversation is under way they
    are just noise taking up the panel's scarce vertical space.
    """
    message = (message or "").strip()
    if not message:
        # `gr.update()` with no arguments leaves the examples as they are — an
        # empty submit must not un-hide them mid-conversation.
        return history, "", gr.update()

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
        gr.update(visible=False),
    )


def panel_header() -> str:
    sub = (
        f'<p class="tw-panel__sub">{profile.twin.subheading}</p>'
        if profile.twin.subheading
        else ""
    )
    return (
        # The grips are absolutely positioned against #twin-panel (the nearest
        # positioned ancestor), so they sit on the panel's top/left edges even
        # though they are emitted here inside the header block.
        '<div class="tw-panel__grip tw-panel__grip--top" data-tw-axis="y"'
        ' title="Drag to resize"></div>'
        '<div class="tw-panel__grip tw-panel__grip--left" data-tw-axis="x"'
        ' title="Drag to resize"></div>'
        '<div class="tw-panel__grip tw-panel__grip--corner" data-tw-axis="both"'
        ' title="Drag to resize"></div>'
        '<div class="tw-panel__head">'
        f'<div><p class="tw-panel__title">{profile.twin.heading}</p>{sub}</div>'
        '<div class="tw-panel__actions">'
        '<button class="tw-panel__expand" type="button"'
        ' title="Expand / restore" aria-label="Expand or restore panel">⤢</button>'
        '<button class="tw-panel__toggle" type="button"'
        ' title="Minimise" aria-label="Minimise panel">—</button>'
        "</div>"
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
            with gr.Column(elem_classes="tw-examples") as examples_box:
                example_buttons = [
                    gr.Button(text, size="sm") for text in profile.twin.examples
                ]
            with gr.Row(elem_classes="tw-composer"):
                msg = gr.Textbox(
                    placeholder="Ask about my experience, skills…",
                    show_label=False,
                    container=False,
                    lines=1,
                    scale=5,
                )
                send = gr.Button("Send", variant="primary", scale=1, elem_classes="tw-send")

    outputs = [chatbot, msg, examples_box]
    msg.submit(respond, [msg, chatbot], outputs)
    send.click(respond, [msg, chatbot], outputs)

    for button, text in zip(example_buttons, profile.twin.examples):
        button.click(lambda t=text: t, None, msg).then(respond, [msg, chatbot], outputs)

    # Gradio 6 does not run `launch(js=...)` — verified in the browser: the hook
    # never fired. The load event does, and it fires after the components are
    # mounted, which is what the panel toggle needs.
    demo.load(None, None, None, js=JS)


if __name__ == "__main__":
    demo.launch(css=build_css(profile.theme), js=JS, theme=gr.themes.Base())
