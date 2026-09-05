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
  display: block !important;
  font-size: clamp(38px, 6vw, 62px);
  font-weight: 700;
  line-height: 1.04;
  letter-spacing: -0.035em;
  margin: 0 0 10px;
  background-image: linear-gradient(100deg, var(--tw-accent) 8%, var(--tw-accent-alt) 82%) !important;
  -webkit-background-clip: text !important;
  background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
}
.tw-hero__role {
  display: block !important;
  font-size: 17px;
  font-weight: 500;
  color: var(--tw-text);
  margin: 0 0 16px;
}
.tw-hero__tagline {
  display: block !important;
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
  display: block !important;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--tw-muted);
  margin-bottom: 10px;
}
.tw-section__title {
  display: block !important;
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
  display: block !important;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11.5px;
  letter-spacing: 0.06em;
  color: var(--tw-muted);
}
.tw-timeline__role {
  display: block !important;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 6px 0 3px;
  color: var(--tw-text);
}
.tw-timeline__org {
  display: block !important;
  font-size: 13.5px;
  color: var(--tw-accent);
  margin: 0 0 10px;
}
.tw-timeline__detail {
  display: block !important;
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
  display: block !important;
  font-size: 16.5px;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 0;
  color: var(--tw-text);
}
.tw-project__blurb {
  display: block !important;
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
  display: block !important;
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
  max-height: min(600px, 82vh) !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 0 !important;
  background: var(--tw-surface) !important;
  border: 1px solid var(--tw-border) !important;
  border-radius: 16px !important;
  overflow: hidden;
  box-shadow: 0 30px 70px -24px rgba(0, 0, 0, 0.72);
}
/* The body carries `display: flex !important` below, so the collapse rule has
   to be !important too or collapsing would leave it visible (and, with the
   height cap lifted, actually taller than the open panel). */
#twin-panel.tw-collapsed .tw-panel__body { display: none !important; }
#twin-panel.tw-collapsed { max-height: none !important; }

.tw-panel__head {
  flex: 0 0 auto;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--tw-border);
  cursor: pointer;
}
#twin-panel.tw-collapsed .tw-panel__head { border-bottom: 0; }
.tw-panel__title {
  display: block !important;
  font-size: 14px;
  font-weight: 600;
  margin: 0;
  color: var(--tw-text) !important;
}
.tw-panel__sub {
  display: block !important;
  font-size: 12px;
  color: var(--tw-muted) !important;
  margin: 2px 0 0;
}
.tw-panel__toggle {
  color: var(--tw-muted) !important;
  font-size: 16px;
  line-height: 1;
  background: none;
  border: 0;
  cursor: pointer;
}
/* Gradio wraps gr.HTML content in its own prose styles and colours the text
   with an !important rule of its own; these ids raise specificity enough to
   win, without which the panel header renders near-black on near-black. */
#twin-panel .tw-panel__head .tw-panel__title { color: var(--tw-text) !important; }
#twin-panel .tw-panel__head .tw-panel__sub { color: var(--tw-muted) !important; }

/* The chat body fills whatever space is left inside the (px-capped) panel;
   the message list scrolls, the examples/composer stay put at the bottom. */
.tw-panel__body {
  display: flex !important;
  flex-direction: column !important;
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
}

#twin-panel .chatbot, #twin-panel .chatbot.block {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  flex: 1 1 auto !important;
  height: auto !important;
  min-height: 120px !important;
  max-height: none !important;
  overflow-y: auto !important;
}

/* Hide Gradio's own chatbot chrome (share/copy toolbar, per-message copy
   buttons) inside the twin panel — it is not part of this design. Scoped
   so it never touches .tw-send, the example buttons, or the panel toggle. */
#twin-panel .icon-button-wrapper,
#twin-panel .message-buttons-left,
#twin-panel .message-buttons-right,
#twin-panel .icon-button,
#twin-panel button[aria-label="Copy conversation"],
#twin-panel button[aria-label="Copy message"],
#twin-panel [aria-label="Copy conversation"],
#twin-panel [aria-label="Copy message"],
#twin-panel button[aria-label="Share"] {
  display: none !important;
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

.tw-examples { flex: 0 0 auto; display: flex; flex-direction: column; gap: 6px; padding: 0 12px 8px; }
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

.tw-composer { flex: 0 0 auto; padding: 10px 12px 12px; gap: 8px !important; }
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

/* Wide screens: give the docked panel its own lane so it stops covering the
   right-hand edge of the content column (it was overlapping a portfolio card).
   Below this width the panel overlays, which is normal for a chat widget. */
@media (min-width: 1200px) {
  .tw-nav__inner, .tw-hero, .tw-section, .tw-footer {
    margin-left: auto;
    margin-right: 434px;
  }
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
    max-height: min(600px, 78vh) !important;
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
  // Gradio mounts its components after this runs, so binding directly to
  // .tw-panel__head / #twin-panel-open would bind to nothing. Delegate from
  // the document instead: it works no matter when those nodes appear, and
  // survives Gradio re-rendering them.
  if (document.body.dataset.twBound) return;
  document.body.dataset.twBound = '1';

  document.addEventListener('click', (e) => {
    const panel = document.getElementById('twin-panel');
    if (!panel) return;

    if (e.target.closest('#twin-panel-open')) {
      e.preventDefault();
      panel.classList.remove('tw-collapsed');
      const box = panel.querySelector('textarea');
      if (box) box.focus();
      return;
    }

    if (e.target.closest('.tw-panel__head')) {
      panel.classList.toggle('tw-collapsed');
    }
  });
}
"""
