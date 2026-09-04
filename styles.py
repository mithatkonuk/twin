"""Styling constants for the digital twin Gradio app."""

GOLD = "#ecad0a"
BLUE = "#209dd7"
PURPLE = "#753991"

EXAMPLES = [
    "Tell me about your background and experience.",
    "What kinds of projects are you working on now?",
    "What are your strongest technical skills?",
    "How can I get in touch with you?",
]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
  --twin-gold: #ecad0a;
  --twin-blue: #209dd7;
  --twin-purple: #a855f7;
  --twin-bg: #08090c;
  --twin-surface: #101216;
  --twin-surface-2: #16181d;
  --twin-chrome: #0c0d10;
  --twin-border: #23262d;
  --twin-border-strong: #33363f;
  --twin-text: #e7e8ec;
  --twin-muted: #6f7280;
  --twin-prompt: #4ade80;
  --twin-grid: rgba(236, 173, 10, 0.045);
}

/* Light mode: same terminal concept, paper-toned instead of black-glass. */
body:not(.dark) {
  --twin-bg: #f1efe9;
  --twin-surface: #fffdf8;
  --twin-surface-2: #f6f3ec;
  --twin-chrome: #ebe7dd;
  --twin-border: #ddd8ca;
  --twin-border-strong: #c4bea9;
  --twin-text: #1c1b18;
  --twin-muted: #85806f;
  --twin-prompt: #16794f;
  --twin-grid: rgba(117, 57, 145, 0.04);
}

footer, .built-with, .show-api, .api-docs { display: none !important; }

html, body, gradio-app { background: var(--twin-bg) !important; }

/* Faint dot-grid, like graph/engineering paper — very quiet */
body {
  background-image: radial-gradient(var(--twin-grid) 1px, transparent 1px) !important;
  background-size: 22px 22px !important;
}

/* ---------- Stable layout ---------- */
.gradio-container {
  background: transparent !important;
  color: var(--twin-text) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  width: 100% !important;
  max-width: 860px !important;
  min-width: 0 !important;
  margin: 0 auto !important;
  padding: 44px 20px 48px !important;
}
.gradio-container .main, .gradio-container .contain, .gradio-container .wrap {
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
}
.gradio-container * { min-width: 0; }

/* ---------- Title: terminal window chrome + prompt line ---------- */
.gradio-container h1 {
  position: relative;
  color: var(--twin-text) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 20px !important;
  font-weight: 500 !important;
  letter-spacing: 0 !important;
  margin: 0 !important;
  padding: 13px 16px !important;
  text-align: left !important;
  background: var(--twin-chrome) !important;
  border: 1px solid var(--twin-border) !important;
  border-bottom: none !important;
}
.gradio-container h1::before {
  content: "";
  display: inline-block;
  width: 36px;
  height: 10px;
  margin-right: 14px;
  vertical-align: middle;
  border-radius: 50%;
  background:
    radial-gradient(circle 4px at 5px 5px, var(--twin-gold) 100%, transparent 101%),
    radial-gradient(circle 4px at 18px 5px, var(--twin-blue) 100%, transparent 101%),
    radial-gradient(circle 4px at 31px 5px, var(--twin-purple) 100%, transparent 101%);
}
.gradio-container h1::after {
  content: "";
  display: inline-block;
  width: 8px;
  height: 15px;
  margin-left: 4px;
  vertical-align: middle;
  background: var(--twin-prompt);
  animation: twin-caret 1.1s steps(1) infinite;
}
@keyframes twin-caret {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}
.gradio-container > .main > .contain > *:first-child::after {
  content: "guest@" attr(data-twin-host) ":~$ connecting to digital twin of Mithat Konuk...";
}
/* Subtitle line rendered as a second terminal row under the title bar */
.gradio-container > .main > .contain > *:first-child {
  position: relative;
  margin-bottom: 22px !important;
}

/* ---------- Sharp corners everywhere (terminal windows don't round) ---------- */
.chatbot, .chatbot *, .block, .form,
button, input, textarea,
.examples button {
  border-radius: 0 !important;
}

.block, .form { background: transparent !important; box-shadow: none !important; }

.chatbot > .block-label,
.chatbot > label,
.chatbot .label-wrap,
.chatbot .block-label,
.chatbot > .label-container {
  display: none !important;
}

/* ---------- Chatbot = terminal body, fused visually to the title bar above ---------- */
.chatbot, .chatbot.block {
  background: var(--twin-surface) !important;
  border: 1px solid var(--twin-border) !important;
  border-top: none !important;
  min-height: 460px !important;
  box-shadow: 0 24px 60px -20px rgba(0, 0, 0, 0.55) !important;
}
body:not(.dark) .chatbot, body:not(.dark) .chatbot.block {
  box-shadow: 0 24px 48px -24px rgba(28, 27, 24, 0.18) !important;
}
.chatbot .placeholder, .chatbot .placeholder * { color: var(--twin-muted) !important; }

/* ---------- Message rows ---------- */
.message-row,
.message-row > div,
.message-row .role,
.message-wrap, .bubble-wrap {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

@keyframes twin-rise {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
.message-row { animation: twin-rise 0.28s ease both; }

.message-row .message,
.message-row .message-bubble,
.message-row .bubble {
  border: 0 !important;
  box-shadow: none !important;
  padding: 11px 15px !important;
  position: relative;
}

/* User: flat panel, mono label, no bubble theatrics — reads like typed input */
.message-row.user-row .message,
.message-row.user-row .message-bubble,
.message-row.user-row .bubble,
.message-row[data-role="user"] .message,
.message-row[data-role="user"] .message-bubble {
  background: var(--twin-surface-2) !important;
  border: 1px solid var(--twin-border) !important;
  border-right: 2px solid var(--twin-blue) !important;
  color: var(--twin-text) !important;
}

/* Assistant: the "twin" — carries the gradient signal marker */
.message-row.bot-row .message,
.message-row.bot-row .message-bubble,
.message-row.bot-row .bubble,
.message-row[data-role="assistant"] .message,
.message-row[data-role="assistant"] .message-bubble {
  background: var(--twin-surface-2) !important;
  color: var(--twin-text) !important;
  padding-left: 30px !important;
}
.message-row.bot-row .message::before,
.message-row.bot-row .bubble::before,
.message-row.bot-row .message-bubble::before,
.message-row[data-role="assistant"] .message::before,
.message-row[data-role="assistant"] .bubble::before,
.message-row[data-role="assistant"] .message-bubble::before {
  content: "";
  position: absolute;
  left: 11px;
  top: 16px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: conic-gradient(from 180deg, var(--twin-gold), var(--twin-blue), var(--twin-purple), var(--twin-gold));
}

/* Suppress the marker on nested bubble instances (keep exactly one) */
.message-row.bot-row .message .message::before,
.message-row.bot-row .message .bubble::before,
.message-row.bot-row .bubble .message::before,
.message-row.bot-row .bubble .bubble::before,
.message-row.bot-row .message-bubble .message::before,
.message-row.bot-row .message-bubble .bubble::before,
.message-row[data-role="assistant"] .message .message::before,
.message-row[data-role="assistant"] .message .bubble::before,
.message-row[data-role="assistant"] .bubble .message::before,
.message-row[data-role="assistant"] .bubble .bubble::before {
  content: none;
}

/* ---------- Typography inside bubbles ---------- */
.message-row .message,
.message-row .message-bubble,
.message-row .bubble {
  font-size: 14.5px !important;
  line-height: 1.6 !important;
}
.message-row .message p,
.message-row .message-bubble p,
.message-row .bubble p,
.message-row .prose p {
  font-size: 14.5px !important;
  line-height: 1.6 !important;
  margin: 0 0 8px !important;
  color: inherit !important;
}
.message-row .message p:last-child,
.message-row .message-bubble p:last-child,
.message-row .bubble p:last-child,
.message-row .prose p:last-child { margin-bottom: 0 !important; }

.message-row .message *,
.message-row .message-bubble *,
.message-row .bubble * {
  background: transparent !important;
  border-color: transparent !important;
  box-shadow: none !important;
  color: inherit !important;
}
.message-row .message a,
.message-row .message-bubble a {
  color: var(--twin-gold) !important;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.message-row .message code,
.message-row .message-bubble code {
  font-family: 'JetBrains Mono', monospace !important;
  background: rgba(255, 255, 255, 0.06) !important;
  padding: 1px 5px !important;
  font-size: 13px !important;
}
body:not(.dark) .message-row .message code,
body:not(.dark) .message-row .message-bubble code {
  background: rgba(0, 0, 0, 0.06) !important;
}

/* ---------- Input row: prompt-style, fused to bottom of terminal ---------- */
.input-row,
.gr-input-row,
.chat-input-row,
form[class*="input"] {
  align-items: stretch !important;
  gap: 0 !important;
  border: 1px solid var(--twin-border) !important;
  border-top: none !important;
  background: var(--twin-chrome) !important;
}

textarea, input[type="text"] {
  background: transparent !important;
  border: 0 !important;
  color: var(--twin-text) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 13.5px !important;
  padding: 15px 16px !important;
  line-height: 1.4 !important;
  min-height: 48px !important;
}
textarea:focus, input[type="text"]:focus {
  outline: none !important;
  box-shadow: none !important;
}
textarea::placeholder, input::placeholder { color: var(--twin-muted) !important; }
textarea::placeholder { content: "$ "; }

/* ---------- Buttons ---------- */
button {
  font-family: 'JetBrains Mono', 'SF Mono', Menlo, monospace !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  border: 1px solid var(--twin-border) !important;
  border-left: 1px solid var(--twin-border) !important;
  background: transparent !important;
  color: var(--twin-muted) !important;
  padding: 0 18px !important;
  min-height: 48px !important;
  align-self: stretch !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
}
button:hover { color: var(--twin-gold) !important; background: rgba(236, 173, 10, 0.06) !important; }
button:active { background: rgba(236, 173, 10, 0.12) !important; }

button.primary,
button[variant="primary"],
button.submit,
button.submit-button,
.submit-button,
button.lg.primary {
  background: var(--twin-gold) !important;
  border-color: var(--twin-gold) !important;
  color: #0c0d10 !important;
}
button.primary:hover,
button.submit:hover,
.submit-button:hover,
button.lg.primary:hover {
  background: #ffc320 !important;
  border-color: #ffc320 !important;
  color: #0c0d10 !important;
}

button.submit svg,
button.submit-button svg,
.submit-button svg,
button.primary svg,
button[variant="primary"] svg {
  width: 17px !important;
  height: 17px !important;
  margin: 0 auto !important;
  display: block !important;
  color: #0c0d10 !important;
  fill: currentColor !important;
  stroke: currentColor !important;
}

/* ---------- Examples: rendered like recent commands ---------- */
.examples, .examples-holder, [data-testid="examples"] {
  background: transparent !important;
  padding: 0 !important;
  margin-top: 18px !important;
}
.examples table, .examples-table { background: transparent !important; border: 0 !important; }
.examples button, .example, .examples td button, [data-testid="examples"] button {
  background: transparent !important;
  border: 1px dashed var(--twin-border-strong) !important;
  color: var(--twin-muted) !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 12.5px !important;
  font-weight: 400 !important;
  padding: 10px 13px !important;
  text-align: left !important;
  min-height: 0 !important;
  align-self: auto !important;
  display: inline-block !important;
  transition: border-color 0.15s ease, color 0.15s ease;
}
.examples button::before, .example::before, [data-testid="examples"] button::before {
  content: "> ";
  color: var(--twin-gold);
}
.examples button:hover, .example:hover, [data-testid="examples"] button:hover {
  border-color: var(--twin-gold) !important;
  border-style: solid !important;
  color: var(--twin-text) !important;
  background: transparent !important;
}

/* ---------- Icon buttons (clear, retry, copy) ---------- */
.icon-button, .chatbot .icon-button {
  color: var(--twin-muted) !important;
  background: transparent !important;
  border: 0 !important;
  min-height: 0 !important;
  align-self: auto !important;
  padding: 4px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}
.icon-button:hover, .chatbot .icon-button:hover { color: var(--twin-gold) !important; }

/* ---------- Scrollbar ---------- */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--twin-bg); }
::-webkit-scrollbar-thumb { background: var(--twin-border-strong); }
::-webkit-scrollbar-thumb:hover { background: var(--twin-gold); }

::selection { background: var(--twin-gold); color: #0c0d10; }

@media (prefers-reduced-motion: reduce) {
  *, .gradio-container h1::after { animation: none !important; opacity: 1 !important; }
  .message-row { animation: none !important; }
}

@media (max-width: 640px) {
  .gradio-container { padding: 28px 12px 36px !important; }
  .gradio-container h1 { font-size: 15px !important; padding: 12px !important; }
}
"""

JS = """
() => {
  document.title = 'Digital Twin ( Mithat Konuk )';

  const host = document.querySelector('.gradio-container');
  if (host) host.setAttribute('data-twin-host', 'mithat-konuk');

  const focusInput = () => {
    const areas = document.querySelectorAll('textarea');
    if (areas.length) areas[areas.length - 1].focus();
  };
  setTimeout(focusInput, 300);

  // Re-focus the message field whenever Gradio re-enables it
  // (i.e. after the assistant finishes responding).
  const watchTextarea = (area) => {
    if (area.dataset.twinWatched) return;
    area.dataset.twinWatched = '1';
    let wasDisabled = area.disabled || area.readOnly;
    new MutationObserver(() => {
      const isDisabled = area.disabled || area.readOnly;
      if (wasDisabled && !isDisabled) area.focus();
      wasDisabled = isDisabled;
    }).observe(area, { attributes: true, attributeFilter: ['disabled', 'readonly'] });
  };

  const scan = () => document.querySelectorAll('textarea').forEach(watchTextarea);
  setTimeout(scan, 500);
  new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
}
"""
