"""
generate_command_summary.py
Parses config.yaml and generates COMMAND_SUMMARY.html — a styled reference table
of all Vangard CLI commands, their arguments, and UI hints.
"""

import yaml
import html
import sys
from pathlib import Path

YAML_INPUT = "config.yaml"
HTML_OUTPUT = "COMMAND_SUMMARY.html"

# ── Widget badge colours ────────────────────────────────────────────────────
WIDGET_COLOURS = {
    "text":          ("#3b82f6", "#dbeafe"),   # blue
    "file-picker":   ("#8b5cf6", "#ede9fe"),   # violet
    "folder-picker": ("#7c3aed", "#f5f3ff"),   # purple
    "checkbox":      ("#10b981", "#d1fae5"),   # green
    "select":        ("#f59e0b", "#fef3c7"),   # amber
    "slider":        ("#ef4444", "#fee2e2"),   # red
    "spinner":       ("#06b6d4", "#cffafe"),   # cyan
}
DEFAULT_WIDGET_COLOUR = ("#6b7280", "#f3f4f6")  # grey


def widget_badge(widget_name: str) -> str:
    fg, bg = WIDGET_COLOURS.get(widget_name, DEFAULT_WIDGET_COLOUR)
    label = html.escape(widget_name)
    return (
        f'<span class="badge" style="background:{bg};color:{fg};'
        f'border:1px solid {fg}33;">{label}</span>'
    )


def format_ui_hints(ui: dict, autocomplete) -> str:
    if not ui and not autocomplete:
        return '<span class="muted">—</span>'

    parts = []

    widget = ui.get("widget", "")
    if widget:
        parts.append(widget_badge(widget))

    if widget == "select":
        choices = ui.get("choices", [])
        if choices:
            formatted = []
            for c in choices:
                if isinstance(c, dict):
                    formatted.append(html.escape(c.get("label", c.get("value", str(c)))))
                else:
                    formatted.append(html.escape(str(c)))
            parts.append(
                '<span class="hint-detail">choices: '
                + ", ".join(f"<code>{v}</code>" for v in formatted)
                + "</span>"
            )

    if widget in ("slider", "spinner"):
        mn = ui.get("min")
        mx = ui.get("max")
        step = ui.get("step")
        bits = []
        if mn is not None:
            bits.append(f"min&nbsp;{mn}")
        if mx is not None:
            bits.append(f"max&nbsp;{mx}")
        if step is not None:
            bits.append(f"step&nbsp;{step}")
        if bits:
            parts.append('<span class="hint-detail">' + " · ".join(bits) + "</span>")

    if widget in ("file-picker",):
        exts = ui.get("extensions")
        mode = ui.get("mode")
        if exts:
            parts.append(
                '<span class="hint-detail">ext: '
                + " ".join(f"<code>{html.escape(e)}</code>" for e in exts)
                + "</span>"
            )
        if mode:
            parts.append(f'<span class="hint-detail">mode: <code>{html.escape(mode)}</code></span>')

    placeholder = ui.get("placeholder")
    if placeholder:
        parts.append(
            f'<span class="hint-placeholder">e.g.&nbsp;<em>{html.escape(placeholder)}</em></span>'
        )

    if autocomplete:
        src = autocomplete.get("source", "")
        types = autocomplete.get("types", [])
        ac_text = f'autocomplete: <code>{html.escape(src)}</code>'
        if types:
            ac_text += " [" + ", ".join(f"<code>{html.escape(t)}</code>" for t in types) + "]"
        parts.append(f'<span class="hint-autocomplete">&#x1F4AC; {ac_text}</span>')

    return '<div class="hint-stack">' + "".join(parts) + "</div>"


def format_arg_row(arg: dict) -> str:
    names = arg.get("names", [])
    primary = names[0] if names else ""
    aliases = names[1:] if len(names) > 1 else []

    is_required = arg.get("required", False) and arg.get("action") != "store_true"
    action = arg.get("action", "")
    if action == "store_true":
        arg_type = "flag"
    else:
        arg_type = arg.get("type", "str")

    nargs = arg.get("nargs")
    if nargs:
        arg_type += f"&nbsp;<code>nargs={nargs}</code>"

    default = arg.get("default")
    default_str = ""
    if default is not None and default != "":
        default_str = f'<span class="arg-default">default: <code>{html.escape(str(default))}</code></span>'

    badge_class = "badge-required" if is_required else "badge-optional"
    badge_label = "required" if is_required else "optional"

    alias_html = ""
    if aliases:
        alias_html = " ".join(
            f'<code class="alias">{html.escape(a)}</code>' for a in aliases
        )

    help_text = html.escape(arg.get("help", ""))

    ui_html = format_ui_hints(arg.get("ui", {}), arg.get("autocomplete"))

    return f"""
      <tr>
        <td class="arg-name-cell">
          <code class="arg-primary">{html.escape(primary)}</code>
          {alias_html}
          <span class="badge {badge_class}">{badge_label}</span>
        </td>
        <td class="arg-type-cell"><code>{arg_type}</code>{default_str}</td>
        <td class="arg-desc-cell">{help_text}</td>
        <td class="arg-ui-cell">{ui_html}</td>
      </tr>"""


def build_html(commands: list) -> str:
    sorted_commands = sorted(commands, key=lambda c: c.get("name", "").lower())

    rows_html = ""
    for cmd in sorted_commands:
        name = cmd.get("name", "")
        desc = html.escape(cmd.get("help", ""))
        cls = cmd.get("class", "")
        cls_short = cls.split(".")[-1] if cls else ""
        arguments = cmd.get("arguments", [])

        required_args = [
            a for a in arguments
            if a.get("required", False) and a.get("action") != "store_true"
        ]
        optional_args = [
            a for a in arguments
            if not a.get("required", False) or a.get("action") == "store_true"
        ]

        req_count = len(required_args)
        opt_count = len(optional_args)
        count_label = []
        if req_count:
            count_label.append(
                f'<span class="badge badge-required">{req_count} required</span>'
            )
        if opt_count:
            count_label.append(
                f'<span class="badge badge-optional">{opt_count} optional</span>'
            )
        count_html = "".join(count_label) if count_label else '<span class="muted">none</span>'

        arg_table = ""
        if arguments:
            arg_rows = "".join(format_arg_row(a) for a in arguments)
            arg_table = f"""
          <details class="arg-details">
            <summary class="arg-summary">
              Arguments&nbsp;&nbsp;{count_html}
            </summary>
            <div class="arg-table-wrap">
              <table class="arg-table">
                <thead>
                  <tr>
                    <th>Name / Flags</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>UI Hint</th>
                  </tr>
                </thead>
                <tbody>{arg_rows}
                </tbody>
              </table>
            </div>
          </details>"""
        else:
            arg_table = '<span class="muted">No arguments.</span>'

        rows_html += f"""
      <tr class="cmd-row">
        <td class="cmd-name-cell">
          <code class="cmd-name">{html.escape(name)}</code>
          <div class="cmd-class">{html.escape(cls_short)}</div>
        </td>
        <td class="cmd-desc-cell">
          <p class="cmd-desc">{desc}</p>
          {arg_table}
        </td>
      </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Vangard Command Reference</title>
  <style>
    /* ── Reset & base ─────────────────────────────────────────────── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    /* ── Dark theme (default) ─────────────────────────────────────── */
    :root, html[data-theme="dark"] {{
      --bg:           #0f1117;
      --surface:      #1a1d27;
      --surface2:     #222534;
      --surface3:     #2b2f42;
      --border:       #2e3348;
      --border-light: #3a3f5c;
      --text:         #e2e5f0;
      --text-muted:   #6b7280;
      --text-dim:     #9ca3af;
      --accent:       #6366f1;
      --accent-glow:  #6366f133;
      --radius:       8px;
      --radius-sm:    4px;
      --font-mono:    "JetBrains Mono", "Fira Code", "Cascadia Code", ui-monospace, monospace;
      --font-sans:    "Inter", system-ui, -apple-system, sans-serif;
      --badge-opt-bg:    #1e293b;
      --badge-opt-color: #64748b;
      --badge-opt-border:#334155;
      --toggle-bg:    #2b2f42;
      --toggle-color: #9ca3af;
      --toggle-border:#3a3f5c;
      --toggle-hover: #3a3f5c;
    }}

    /* ── Light theme ──────────────────────────────────────────────── */
    html[data-theme="light"] {{
      --bg:           #f5f6fa;
      --surface:      #ffffff;
      --surface2:     #eef0f7;
      --surface3:     #e4e7f2;
      --border:       #d5d9ec;
      --border-light: #c0c6e0;
      --text:         #1a1d27;
      --text-muted:   #6b7280;
      --text-dim:     #4b5563;
      --accent:       #4f46e5;
      --accent-glow:  #4f46e514;
      --badge-opt-bg:    #e2e8f0;
      --badge-opt-color: #475569;
      --badge-opt-border:#94a3b8;
      --toggle-bg:    #ffffff;
      --toggle-color: #4b5563;
      --toggle-border:#d5d9ec;
      --toggle-hover: #e4e7f2;
    }}

    body {{
      font-family: var(--font-sans);
      background: var(--bg);
      color: var(--text);
      font-size: 14px;
      line-height: 1.6;
      padding: 2rem 1.5rem 4rem;
      transition: background .2s, color .2s;
    }}

    /* ── Page header ──────────────────────────────────────────────── */
    .page-header {{
      max-width: 1100px;
      margin: 0 auto 2.5rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid var(--border);
      display: grid;
      grid-template-columns: 1fr auto;
      align-items: start;
      gap: 1rem;
    }}
    .page-header-text h1 {{
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text);
    }}
    .page-header-text h1 span {{
      color: var(--accent);
    }}
    .page-subtitle {{
      margin-top: .35rem;
      color: var(--text-dim);
      font-size: .9rem;
    }}
    .page-meta {{
      margin-top: .75rem;
      display: flex;
      gap: .75rem;
      flex-wrap: wrap;
      font-size: .8rem;
      color: var(--text-muted);
    }}
    .page-meta span {{ display: flex; align-items: center; gap: .3rem; }}

    /* ── Theme toggle button ──────────────────────────────────────── */
    #theme-toggle {{
      margin-top: .25rem;
      display: inline-flex;
      align-items: center;
      gap: .4rem;
      padding: .4rem .75rem;
      background: var(--toggle-bg);
      color: var(--toggle-color);
      border: 1px solid var(--toggle-border);
      border-radius: 6px;
      font-family: var(--font-sans);
      font-size: .8rem;
      cursor: pointer;
      white-space: nowrap;
      transition: background .15s, color .15s, border-color .15s;
    }}
    #theme-toggle:hover {{
      background: var(--toggle-hover);
      color: var(--text);
    }}
    #theme-toggle .icon {{ font-size: 1rem; line-height: 1; }}

    /* ── Main table ───────────────────────────────────────────────── */
    .wrap {{
      max-width: 1100px;
      margin: 0 auto;
      overflow-x: auto;
    }}
    table.main-table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
    }}
    table.main-table thead th {{
      background: var(--surface3);
      padding: .7rem 1rem;
      text-align: left;
      font-size: .75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: var(--text-dim);
      border-bottom: 1px solid var(--border);
    }}
    table.main-table thead th:first-child {{ width: 190px; }}
    .cmd-row:not(:last-child) td {{ border-bottom: 1px solid var(--border); }}
    .cmd-row:hover td {{ background: var(--surface2); }}
    .cmd-row td {{ padding: 1rem; vertical-align: top; }}

    /* ── Command name cell ────────────────────────────────────────── */
    .cmd-name-cell {{ width: 190px; }}
    .cmd-name {{
      font-family: var(--font-mono);
      font-size: .88rem;
      font-weight: 600;
      color: var(--accent);
      background: var(--accent-glow);
      padding: .2em .5em;
      border-radius: var(--radius-sm);
      white-space: nowrap;
    }}
    .cmd-class {{
      margin-top: .4rem;
      font-size: .72rem;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }}

    /* ── Command description cell ─────────────────────────────────── */
    .cmd-desc {{ color: var(--text); margin-bottom: .6rem; font-size: .88rem; }}

    /* ── Args details/summary ─────────────────────────────────────── */
    .arg-details {{ margin-top: .4rem; }}
    .arg-summary {{
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: .5rem;
      font-size: .8rem;
      color: var(--text-dim);
      user-select: none;
      padding: .25rem 0;
      list-style: none;
    }}
    .arg-summary::-webkit-details-marker {{ display: none; }}
    .arg-summary::before {{
      content: "▶";
      font-size: .65rem;
      transition: transform .15s;
      color: var(--accent);
    }}
    details[open] .arg-summary::before {{ transform: rotate(90deg); }}
    .arg-summary:hover {{ color: var(--text); }}

    /* ── Argument inner table ─────────────────────────────────────── */
    .arg-table-wrap {{
      margin-top: .6rem;
      overflow-x: auto;
      border: 1px solid var(--border-light);
      border-radius: var(--radius-sm);
    }}
    table.arg-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: .8rem;
    }}
    table.arg-table thead th {{
      background: var(--surface3);
      padding: .45rem .75rem;
      text-align: left;
      font-size: .7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: .07em;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
    }}
    table.arg-table tbody tr:not(:last-child) td {{
      border-bottom: 1px solid var(--border);
    }}
    table.arg-table tbody tr:hover td {{ background: var(--surface3); }}
    table.arg-table td {{ padding: .5rem .75rem; vertical-align: top; }}

    .arg-name-cell {{ width: 220px; white-space: nowrap; }}
    .arg-primary {{
      font-family: var(--font-mono);
      font-size: .82rem;
      color: var(--text);
    }}
    .alias {{
      font-family: var(--font-mono);
      font-size: .75rem;
      color: var(--text-muted);
      margin-left: .25rem;
    }}
    .arg-type-cell {{
      width: 130px;
      font-family: var(--font-mono);
      font-size: .78rem;
      color: var(--text-dim);
      white-space: nowrap;
    }}
    .arg-default {{
      display: block;
      font-size: .72rem;
      color: var(--text-muted);
      margin-top: .2rem;
    }}
    .arg-desc-cell {{ color: var(--text-dim); font-size: .8rem; }}
    .arg-ui-cell   {{ width: 260px; }}

    /* ── Badges ───────────────────────────────────────────────────── */
    .badge {{
      display: inline-block;
      font-size: .68rem;
      font-weight: 600;
      padding: .15em .45em;
      border-radius: 3px;
      letter-spacing: .04em;
      white-space: nowrap;
    }}
    .badge-required {{
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #f59e0b44;
    }}
    .badge-optional {{
      background: var(--badge-opt-bg);
      color: var(--badge-opt-color);
      border: 1px solid var(--badge-opt-border);
    }}

    /* ── UI hint stack ────────────────────────────────────────────── */
    .hint-stack {{
      display: flex;
      flex-direction: column;
      gap: .3rem;
    }}
    .hint-detail, .hint-placeholder, .hint-autocomplete {{
      font-size: .74rem;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }}
    .hint-placeholder {{ font-style: italic; font-family: var(--font-sans); color: var(--text-muted); }}
    .hint-autocomplete {{ color: #a78bfa; font-family: var(--font-sans); }}

    /* ── Misc ─────────────────────────────────────────────────────── */
    code {{
      font-family: var(--font-mono);
      font-size: .85em;
      background: var(--surface3);
      padding: .1em .3em;
      border-radius: 3px;
      color: var(--text);
    }}
    .muted {{ color: var(--text-muted); font-size: .8rem; }}

    /* ── Legend ───────────────────────────────────────────────────── */
    .legend {{
      max-width: 1100px;
      margin: 1.75rem auto 0;
      display: flex;
      flex-wrap: wrap;
      gap: .6rem 1.25rem;
      font-size: .78rem;
      color: var(--text-muted);
    }}
    .legend-item {{ display: flex; align-items: center; gap: .4rem; }}

    @media (max-width: 700px) {{
      body {{ padding: 1rem .75rem 3rem; }}
      table.main-table thead th:first-child,
      .cmd-name-cell {{ width: 130px; }}
    }}
  </style>
</head>
<body>

<header class="page-header">
  <div class="page-header-text">
    <h1>Vangard <span>Command Reference</span></h1>
    <p class="page-subtitle">Auto-generated from <code>config.yaml</code> · All CLI commands, arguments, and UI hints.</p>
    <div class="page-meta">
      <span>&#x1F4CB; {len(sorted_commands)} commands</span>
      <span>&#x1F504; Run <code>npm run generate-docs</code> to regenerate</span>
    </div>
  </div>
  <button id="theme-toggle" onclick="toggleTheme()" title="Toggle light/dark theme">
    <span class="icon" id="theme-icon">☀️</span>
    <span id="theme-label">Light</span>
  </button>
</header>

<div class="wrap">
  <table class="main-table">
    <thead>
      <tr>
        <th>Command</th>
        <th>Description &amp; Arguments</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</div>

<div class="legend">
  <div class="legend-item"><span class="badge badge-required">required</span> Required argument</div>
  <div class="legend-item"><span class="badge badge-optional">optional</span> Optional argument</div>
  {"".join(
    f'<div class="legend-item">{widget_badge(w)} Widget type</div>'
    for w in WIDGET_COLOURS
  )}
</div>

<script>
  (function () {{
    var saved = localStorage.getItem('vangard-theme') || 'dark';
    applyTheme(saved);
  }})();

  function applyTheme(theme) {{
    document.documentElement.setAttribute('data-theme', theme);
    var icon  = document.getElementById('theme-icon');
    var label = document.getElementById('theme-label');
    if (icon)  icon.textContent  = theme === 'dark' ? '☀️' : '🌙';
    if (label) label.textContent = theme === 'dark' ? 'Light' : 'Dark';
    localStorage.setItem('vangard-theme', theme);
  }}

  function toggleTheme() {{
    var current = document.documentElement.getAttribute('data-theme') || 'dark';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  }}
</script>

</body>
</html>"""


def main():
    yaml_path = Path(YAML_INPUT)
    if not yaml_path.exists():
        print(f"Error: '{YAML_INPUT}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    commands = data.get("commands", [])
    if not commands:
        print("Warning: no commands found in config.yaml")

    html_content = build_html(commands)

    output_path = Path(HTML_OUTPUT)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated '{HTML_OUTPUT}' ({len(commands)} commands)")


if __name__ == "__main__":
    main()
