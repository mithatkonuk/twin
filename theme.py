"""Build the stylesheet from the configured palette.

`CSS_TEMPLATE` references `--tw-*` custom properties only — no colour literals.
`build_css` emits the `:root` block from the Theme model and prepends it, so
every colour on the page traces back to profile.yaml.
"""

from __future__ import annotations

from profile import Theme

CSS_TEMPLATE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ---------- Reset the Gradio chrome we do not want ---------- */
footer, .built-with, .show-api, .api-docs { display: none !important; }

html, body, gradio-app {
  background: var(--tw-bg) !important;
  color: var(--tw-text);
}

/* Frosted-glass backdrop: a soft white bloom at the top fading into a cool
   grey-blue, so the translucent cards have something to blur against. */
body {
  background-image:
    radial-gradient(1100px 620px at 78% -8%, color-mix(in srgb, var(--tw-highlight) 90%, transparent), transparent 70%),
    radial-gradient(900px 700px at -10% 110%, color-mix(in srgb, var(--tw-accent-alt) 28%, transparent), transparent 70%),
    linear-gradient(180deg, var(--tw-bg) 0%, color-mix(in srgb, var(--tw-accent-alt) 18%, var(--tw-bg)) 100%) !important;
  background-attachment: fixed !important;
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
  backdrop-filter: blur(18px) saturate(140%);
  background: color-mix(in srgb, var(--tw-highlight) 55%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--tw-highlight) 70%, var(--tw-border));
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
.tw-nav__link--cta {
  color: var(--tw-highlight);
  background: var(--tw-accent);
  border-radius: 999px;
  padding: 6px 14px;
  font-weight: 500;
  box-shadow: 0 8px 20px -10px color-mix(in srgb, var(--tw-accent) 70%, transparent);
}
.tw-nav__link--cta:hover { color: var(--tw-highlight); background: color-mix(in srgb, var(--tw-accent) 85%, var(--tw-text)); }

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
    color-mix(in srgb, var(--tw-highlight) 85%, transparent) 0%,
    transparent 68%
  );
  filter: blur(20px);
}
.tw-hero__text { position: relative; max-width: 560px; }
.tw-hero__eyebrow {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--tw-text);
  background: var(--tw-highlight);
  border: 0;
  border-radius: 999px;
  padding: 6px 13px;
  margin-bottom: 22px;
  box-shadow: 0 6px 18px -10px color-mix(in srgb, var(--tw-accent) 45%, transparent);
}
.tw-hero__name {
  display: block !important;
  font-size: clamp(40px, 6.4vw, 68px);
  font-weight: 300;
  line-height: 1.04;
  letter-spacing: -0.04em;
  margin: 0 0 12px;
  background-image: linear-gradient(100deg, var(--tw-text) 35%, var(--tw-accent-alt) 100%) !important;
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
  border: 1px solid var(--tw-highlight);
  box-shadow:
    0 0 0 7px color-mix(in srgb, var(--tw-highlight) 55%, transparent),
    0 26px 60px -24px color-mix(in srgb, var(--tw-accent) 55%, transparent);
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
  font-size: 30px;
  font-weight: 400;
  letter-spacing: -0.025em;
  margin: 0 0 24px;
  color: var(--tw-text);
}
/* Frosted glass: a translucent white-to-surface wash, a bright hairline edge,
   an inset top highlight and a soft accent-tinted drop shadow. */
.tw-card {
  background: linear-gradient(
    160deg,
    color-mix(in srgb, var(--tw-highlight) 82%, transparent) 0%,
    color-mix(in srgb, var(--tw-surface) 58%, transparent) 100%
  );
  border: 1px solid color-mix(in srgb, var(--tw-highlight) 90%, transparent);
  border-radius: 22px;
  padding: 28px 30px;
  backdrop-filter: blur(20px) saturate(140%);
  -webkit-backdrop-filter: blur(20px) saturate(140%);
  box-shadow:
    inset 0 1px 0 var(--tw-highlight),
    0 22px 48px -30px color-mix(in srgb, var(--tw-accent) 45%, transparent);
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
  border-left: 1px solid color-mix(in srgb, var(--tw-accent-alt) 55%, transparent);
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
  background: var(--tw-highlight);
  border: 2px solid var(--tw-accent);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--tw-accent-alt) 25%, transparent);
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
  background: color-mix(in srgb, var(--tw-highlight) 70%, transparent);
  border: 1px solid color-mix(in srgb, var(--tw-highlight) 90%, var(--tw-border));
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
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.tw-project:hover {
  transform: translateY(-3px);
  box-shadow:
    inset 0 1px 0 var(--tw-highlight),
    0 30px 60px -30px color-mix(in srgb, var(--tw-accent) 60%, transparent);
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
.tw-project__link:hover { color: var(--tw-text); }

/* ---------- Contact ---------- */
/* The one deep moment on the page: the glass card fades from white into the
   accent navy, and the links sit on that band as round glass buttons. */
.tw-contact .tw-card {
  padding-bottom: 34px;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--tw-highlight) 82%, transparent) 0%,
    color-mix(in srgb, var(--tw-surface) 60%, transparent) 30%,
    color-mix(in srgb, var(--tw-accent) 70%, var(--tw-accent-alt)) 72%,
    var(--tw-accent) 100%
  );
  box-shadow:
    inset 0 1px 0 var(--tw-highlight),
    0 30px 60px -30px color-mix(in srgb, var(--tw-accent) 70%, transparent);
}
.tw-contact__intro {
  display: block !important;
  font-size: 15px;
  line-height: 1.74;
  color: var(--tw-muted);
  margin: 0 0 72px;
}
.tw-contact__links { display: flex; flex-wrap: wrap; gap: 10px; }
.tw-contact__link {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--tw-highlight);
  text-decoration: none;
  background: color-mix(in srgb, var(--tw-highlight) 14%, transparent);
  border: 1px solid color-mix(in srgb, var(--tw-highlight) 38%, transparent);
  border-radius: 999px;
  padding: 10px 20px;
  backdrop-filter: blur(10px);
  transition: background 0.18s ease, border-color 0.18s ease;
}
.tw-contact__link:hover {
  background: color-mix(in srgb, var(--tw-highlight) 26%, transparent);
  border-color: color-mix(in srgb, var(--tw-highlight) 60%, transparent);
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
/* Size lives in two custom properties so the drag handles (and the persisted
   localStorage value) can set it from JS without fighting the !important rules
   Gradio's own styles force us into. The clamps keep any restored size inside
   the current viewport, which is what makes the panel survive a window
   resize or a move to a smaller screen. */
#twin-panel {
  position: fixed !important;
  right: 22px;
  bottom: 22px;
  z-index: 60;
  width: clamp(300px, var(--tw-panel-w, 400px), calc(100vw - 44px)) !important;
  height: clamp(260px, var(--tw-panel-h, 620px), calc(100vh - 44px)) !important;
  max-height: calc(100vh - 44px) !important;
  max-width: calc(100vw - 44px) !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 0 !important;
  background: color-mix(in srgb, var(--tw-surface) 80%, transparent) !important;
  border: 1px solid var(--tw-highlight) !important;
  border-radius: 24px !important;
  overflow: hidden;
  backdrop-filter: blur(24px) saturate(150%);
  -webkit-backdrop-filter: blur(24px) saturate(150%);
  box-shadow:
    inset 0 1px 0 var(--tw-highlight),
    0 34px 80px -30px color-mix(in srgb, var(--tw-accent) 60%, transparent);
}
/* While dragging, suppress transitions and text selection so the drag reads
   as a direct manipulation rather than a lagging animation. */
#twin-panel.tw-resizing { transition: none !important; }
body.tw-resizing-active { user-select: none !important; cursor: nwse-resize !important; }

/* The body carries `display: flex !important` below, so the collapse rule has
   to be !important too or collapsing would leave it visible (and, with the
   height cap lifted, actually taller than the open panel). */
#twin-panel.tw-collapsed .tw-panel__body { display: none !important; }
#twin-panel.tw-collapsed { height: auto !important; max-height: none !important; }
#twin-panel.tw-collapsed .tw-panel__grip { display: none !important; }

/* Maximised: one click to a near-full-height reading pane, one click back. */
#twin-panel.tw-maximised {
  width: min(760px, calc(100vw - 44px)) !important;
  height: calc(100vh - 44px) !important;
}

/* ---------- Resize handles ---------- */
/* The panel is anchored bottom-right, so it grows up and to the left: handles
   sit on the top and left edges plus the top-left corner. */
/* Gradio gives every block `position: relative`, which would make the header's
   own wrapper the containing block for the grips and pin them to the header
   strip instead of the panel edges. Neutralise it on the header wrapper only
   (the first child of the panel) so the grips resolve against #twin-panel. */
#twin-panel > *:first-child,
#twin-panel > *:first-child > * {
  position: static !important;
  overflow: visible !important;
}

.tw-panel__grip {
  position: absolute;
  z-index: 3;
  touch-action: none;
}
.tw-panel__grip--top { top: 0; left: 14px; right: 14px; height: 8px; cursor: ns-resize; }
.tw-panel__grip--left { left: 0; top: 14px; bottom: 14px; width: 8px; cursor: ew-resize; }
.tw-panel__grip--corner {
  top: 0;
  left: 0;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
  border-top: 2px solid transparent;
  border-left: 2px solid transparent;
  border-top-left-radius: 24px;
  transition: border-color 0.15s ease;
}
#twin-panel:hover .tw-panel__grip--corner {
  border-color: color-mix(in srgb, var(--tw-accent) 55%, transparent);
}

.tw-panel__head {
  flex: 0 0 auto;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 16px 14px 22px;
  border-bottom: 1px solid color-mix(in srgb, var(--tw-highlight) 70%, var(--tw-border));
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
.tw-panel__actions { display: flex; align-items: center; gap: 4px; flex: 0 0 auto; }
.tw-panel__toggle, .tw-panel__expand {
  color: var(--tw-muted) !important;
  font-size: 15px;
  line-height: 1;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: 0;
  border-radius: 999px;
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
}
.tw-panel__toggle:hover, .tw-panel__expand:hover {
  color: var(--tw-text) !important;
  background: var(--tw-highlight) !important;
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

/* Gradio renders the Chatbot inside a wrapper block and stamps its `height`
   (400px by default) on that wrapper as an inline style — which no `.chatbot`
   selector reaches, so the message list stayed 400px tall and left dead space
   above the composer in a taller panel. Target the body's first child, which
   is that wrapper, and let it take whatever room the panel has. */
#twin-panel .tw-panel__body > *:first-child,
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
  background: var(--tw-highlight) !important;
  color: var(--tw-text) !important;
  border: 1px solid color-mix(in srgb, var(--tw-highlight) 60%, var(--tw-border)) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 20px -16px color-mix(in srgb, var(--tw-accent) 50%, transparent) !important;
  font-size: 13.5px !important;
  line-height: 1.62 !important;
  padding: 10px 13px !important;
}
/* Gradio nests a bubble three deep (.message-row.bubble > .message >
   .message). All three match the rule above; with a shadow on each the answer
   read as a card inside a card. Only the innermost one keeps the bubble look. */
#twin-panel .message-row.bubble,
#twin-panel .message:has(> .message) {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
}
#twin-panel .user-row .message:not(:has(> .message)) {
  background: color-mix(in srgb, var(--tw-accent-alt) 22%, var(--tw-highlight)) !important;
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
/* Only `p` used to be recoloured, so every other element the model's markdown
   produces — headings, `strong`, list items, blockquotes, table cells — kept
   Gradio's own prose colour, which is tuned for a light theme and renders
   unevenly against this palette. That is why an answer showed a few
   readable paragraphs and the rest as barely-visible grey. Recolour the whole
   subtree, then restore the two things that are deliberately not body text. */
#twin-panel .message,
#twin-panel .message *,
#twin-panel .message .prose,
#twin-panel .message .prose * {
  color: var(--tw-text) !important;
}
#twin-panel .message h1, #twin-panel .message h2, #twin-panel .message h3,
#twin-panel .message h4, #twin-panel .message h5, #twin-panel .message h6 {
  font-size: 14.5px !important;
  font-weight: 650 !important;
  line-height: 1.4 !important;
  margin: 12px 0 6px !important;
}
#twin-panel .message ul, #twin-panel .message ol {
  margin: 0 0 8px !important;
  padding-left: 18px !important;
}
#twin-panel .message li { margin: 0 0 4px !important; }
#twin-panel .message code, #twin-panel .message pre {
  background: var(--tw-surface-alt) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 12px !important;
}
#twin-panel .message blockquote {
  border-left: 2px solid var(--tw-border) !important;
  padding-left: 10px !important;
  color: var(--tw-muted) !important;
}

/* Gradio also fades each rendered chunk in. In a panel this short a chunk that
   finishes while the list is scrolling can settle at a partial opacity and stay
   there, which reads as the same washed-out text. Nothing here depends on that
   animation. */
#twin-panel .message,
#twin-panel .message *,
#twin-panel .message-row,
#twin-panel .message-row * {
  animation: none !important;
  opacity: 1 !important;
  filter: none !important;
}

/* Long words, URLs, tables and code blocks must not push the bubble wider than
   the panel — at 300px that is the difference between readable and clipped. */
#twin-panel .message, #twin-panel .message * {
  overflow-wrap: anywhere;
  word-break: break-word;
  max-width: 100% !important;
}
#twin-panel .message pre, #twin-panel .message table {
  display: block;
  overflow-x: auto;
  white-space: pre-wrap;
}

.tw-examples { flex: 0 0 auto; display: flex; flex-direction: column; gap: 6px; padding: 0 12px 8px; }
/* `visible=False` from the chat callback must win over the `display: flex`
   above, whichever hide class this Gradio version applies. */
.tw-examples.hide, .tw-examples.hidden { display: none !important; }
.tw-examples button {
  justify-content: flex-start !important;
  text-align: left !important;
  font-size: 12.5px !important;
  color: var(--tw-muted) !important;
  background: color-mix(in srgb, var(--tw-highlight) 75%, transparent) !important;
  border: 1px solid color-mix(in srgb, var(--tw-highlight) 80%, var(--tw-border)) !important;
  border-radius: 14px !important;
  padding: 9px 13px !important;
  min-height: 0 !important;
  transition: color 0.15s ease, border-color 0.15s ease;
}
.tw-examples button:hover {
  color: var(--tw-text) !important;
  border-color: color-mix(in srgb, var(--tw-accent) 55%, var(--tw-border)) !important;
}

/* ---------- Composer ---------- */
/* One rounded glass bar: the textarea fills it and the Send pill sits inside
   on the right, bottom-aligned so it stays put as the input grows. The bar
   (not the textarea) carries the border and focus ring. Gradio gives every
   scaled child `min-width: min(160px, 100%)` and lets rows wrap; both are
   overridden or the button drops below the input in a narrow panel. */
#twin-panel .tw-composer {
  flex: 0 0 auto;
  flex-wrap: nowrap !important;
  align-items: flex-end !important;
  gap: 6px !important;
  /* Gradio rows are `width: 100%`; with side margins that overflows the panel. */
  width: auto !important;
  align-self: stretch;
  box-sizing: border-box;
  margin: 6px 12px 12px !important;
  padding: 5px !important;
  background: var(--tw-highlight) !important;
  border: 1px solid var(--tw-border) !important;
  border-radius: 22px !important;
  box-shadow: 0 10px 26px -18px color-mix(in srgb, var(--tw-accent) 55%, transparent);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
#twin-panel .tw-composer:focus-within {
  border-color: color-mix(in srgb, var(--tw-accent) 55%, var(--tw-border)) !important;
  box-shadow:
    0 0 0 3px color-mix(in srgb, var(--tw-accent-alt) 28%, transparent),
    0 10px 26px -18px color-mix(in srgb, var(--tw-accent) 55%, transparent);
}
#twin-panel .tw-composer > *:not(.tw-send) {
  flex: 1 1 auto !important;
  min-width: 0 !important;
}
#twin-panel textarea, #twin-panel input[type="text"] {
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  color: var(--tw-text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13.5px !important;
  line-height: 1.45 !important;
  padding: 9px 10px !important;
  min-height: 38px !important;
  resize: none !important;
  /* Gradio's autosize can measure before the panel has its width and stamp a
     huge inline height; cap it so the composer never swallows the panel. */
  max-height: 120px !important;
}
#twin-panel textarea:focus { outline: none !important; box-shadow: none !important; }
#twin-panel textarea::placeholder { color: var(--tw-muted) !important; }

#twin-panel button.primary, #twin-panel .tw-send {
  flex: 0 0 auto !important;
  width: auto !important;
  min-width: 0 !important;
  height: 38px !important;
  min-height: 38px !important;
  padding: 0 18px !important;
  background: var(--tw-accent) !important;
  border: 0 !important;
  border-radius: 999px !important;
  color: var(--tw-highlight) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  box-shadow: 0 6px 16px -8px color-mix(in srgb, var(--tw-accent) 80%, transparent);
}
#twin-panel button.primary:hover, #twin-panel .tw-send:hover {
  background: color-mix(in srgb, var(--tw-accent) 85%, var(--tw-text)) !important;
}

/* ---------- Scrollbar + selection ---------- */
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: color-mix(in srgb, var(--tw-accent-alt) 50%, transparent); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--tw-accent-alt); }
::selection { background: var(--tw-accent); color: var(--tw-highlight); }

@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
  .tw-project:hover { transform: none; }
}

/* Wide screens: give the docked panel its own lane so it stops covering the
   right-hand edge of the content column (it was overlapping a portfolio card).
   The lane tracks the panel's own width so a modest resize still keeps the
   content clear — but it stops at 454px. Past that the panel overlays instead,
   which is the normal behaviour for a chat widget and avoids crushing the
   article column down to a couple of words per line. */
@media (min-width: 1200px) {
  .tw-nav__inner, .tw-hero, .tw-section, .tw-footer {
    margin-left: auto;
    margin-right: min(calc(var(--tw-panel-w, 400px) + 54px), 454px);
    transition: margin-right 0.12s ease;
  }
}

/* Between the wide lane and the mobile sheet the panel overlays the content
   (normal for a chat widget) but must not outgrow the viewport. */
@media (max-width: 1199px) {
  #twin-panel { width: clamp(300px, var(--tw-panel-w, 400px), calc(100vw - 44px)) !important; }
}

@media (max-width: 780px) {
  .tw-hero { flex-direction: column-reverse; align-items: flex-start; gap: 28px; padding-top: 56px; }
  .tw-hero__photo { width: 116px; height: 116px; }
  .tw-nav__links { gap: 14px; }
  /* Mobile: a bottom sheet. Dragging a corner on a touch device fights the
     page scroll, so the handles go away and the height follows the viewport
     (dvh so the iOS URL bar does not clip the composer). */
  #twin-panel, #twin-panel.tw-maximised {
    right: 0;
    left: 0;
    bottom: 0;
    width: auto !important;
    max-width: none !important;
    border-radius: 24px 24px 0 0;
    height: clamp(260px, var(--tw-panel-h, 70dvh), 85dvh) !important;
    max-height: 85dvh !important;
  }
  #twin-panel .tw-panel__grip { display: none !important; }
  .tw-panel__head { padding-left: 16px; }
  .tw-footer { padding-bottom: 180px; }
}

/* Short windows (a laptop with devtools open, a split screen): the composer is
   the one thing that must never be pushed out of view. */
@media (max-height: 520px) {
  #twin-panel, #twin-panel.tw-maximised { height: calc(100vh - 16px) !important; bottom: 8px; }
  .tw-examples { display: none !important; }
}
"""


def build_css(theme: Theme) -> str:
    """Render the palette into a :root block and prepend it to the template."""
    lines = [
        f"  --tw-{field.replace('_', '-')}: {value};"
        for field, value in theme.model_dump().items()
    ]
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

  const MIN_W = 300, MIN_H = 260, STORE = 'tw-panel-size';
  const root = document.documentElement;

  // The size lives on :root, not on the panel, because the wide-screen content
  // lane reads the same custom property to keep itself clear of the panel.
  // Gradio re-renders the panel node; :root survives that.
  const maxW = () => Math.max(MIN_W, window.innerWidth - 44);
  const maxH = () => Math.max(MIN_H, window.innerHeight - 44);
  const clamp = (v, lo, hi) => Math.min(Math.max(v, lo), hi);

  const apply = (w, h) => {
    root.style.setProperty('--tw-panel-w', clamp(w, MIN_W, maxW()) + 'px');
    root.style.setProperty('--tw-panel-h', clamp(h, MIN_H, maxH()) + 'px');
  };

  let size = { w: 400, h: 620 };
  try {
    const saved = JSON.parse(localStorage.getItem(STORE) || 'null');
    if (saved && saved.w > 0 && saved.h > 0) size = saved;
  } catch (err) { /* private mode / blocked storage - keep the default */ }
  apply(size.w, size.h);

  const save = () => {
    try { localStorage.setItem(STORE, JSON.stringify(size)); } catch (err) {}
  };

  // Re-clamp on window resize so a size saved on a big monitor does not leave
  // the panel hanging off a small one.
  window.addEventListener('resize', () => apply(size.w, size.h));

  // ---- Drag to resize -------------------------------------------------
  // The panel is anchored bottom-right, so dragging the top/left edges toward
  // the top-left grows it: the delta is subtracted, not added.
  let drag = null;

  document.addEventListener('pointerdown', (e) => {
    const grip = e.target.closest('.tw-panel__grip');
    const panel = document.getElementById('twin-panel');
    if (!grip || !panel) return;
    e.preventDefault();

    const rect = panel.getBoundingClientRect();
    drag = {
      axis: grip.dataset.twAxis || 'both',
      x: e.clientX, y: e.clientY, w: rect.width, h: rect.height,
    };
    panel.classList.remove('tw-maximised');
    panel.classList.add('tw-resizing');
    document.body.classList.add('tw-resizing-active');
    // Capture keeps the drag alive when the pointer leaves the 8px handle.
    // Not every pointer source supports it; the document-level move/up
    // listeners cover the drag either way.
    try { grip.setPointerCapture(e.pointerId); } catch (err) {}
  });

  document.addEventListener('pointermove', (e) => {
    if (!drag) return;
    if (drag.axis !== 'y') size.w = clamp(drag.w + (drag.x - e.clientX), MIN_W, maxW());
    if (drag.axis !== 'x') size.h = clamp(drag.h + (drag.y - e.clientY), MIN_H, maxH());
    apply(size.w, size.h);
  });

  const endDrag = () => {
    if (!drag) return;
    drag = null;
    document.body.classList.remove('tw-resizing-active');
    const panel = document.getElementById('twin-panel');
    if (panel) panel.classList.remove('tw-resizing');
    save();
  };
  document.addEventListener('pointerup', endDrag);
  document.addEventListener('pointercancel', endDrag);

  // ---- Clicks ---------------------------------------------------------
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

    // Checked before the header rule below, which would otherwise collapse the
    // panel as the click bubbles out of the button.
    if (e.target.closest('.tw-panel__expand')) {
      e.preventDefault();
      e.stopPropagation();
      panel.classList.remove('tw-collapsed');
      panel.classList.toggle('tw-maximised');
      return;
    }

    if (e.target.closest('.tw-panel__head')) {
      panel.classList.toggle('tw-collapsed');
    }
  });

  // A resize handle lives on the header edges; a drag that ends on the header
  // must not also register as the collapse click.
  document.addEventListener('click', (e) => {
    if (e.target.closest('.tw-panel__grip')) e.stopPropagation();
  }, true);
}
"""
