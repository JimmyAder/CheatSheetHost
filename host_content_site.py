#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import re


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_FILE = BASE_DIR / "site_template.html"
PAGES_DIR = BASE_DIR / "pages"
RESERVED_SLUGS = {"", "index.html", "api", "api/pages"}
MAX_JSON_SIZE = 512 * 1024  # 512 KB
DEFAULT_PORT = 8766


def is_safe_slug(slug: str) -> bool:
    return bool(re.fullmatch(r"[a-zA-Z0-9._-]+", slug)) and slug not in RESERVED_SLUGS


def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(str(url).strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False
    
    
def get_local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        sock.close()


def ensure_defaults() -> None:
    PAGES_DIR.mkdir(exist_ok=True)
    if not TEMPLATE_FILE.exists():
        TEMPLATE_FILE.write_text(DEFAULT_TEMPLATE, encoding="utf-8")
    default_page = PAGES_DIR / "ctf-cheatsheet.json"
    
    # Check if any .json file exists in the directory
    if not any(PAGES_DIR.glob("*.json")):
        default_page = PAGES_DIR / "ctf-cheatsheet.json"
        default_page.write_text(json.dumps(DEFAULT_PAGE, indent=2), encoding="utf-8")

    # default_page = PAGES_DIR / "ctf-cheatsheet.json"
    # if not default_page.exists():
    #     default_page.write_text(json.dumps(DEFAULT_PAGE, indent=2), encoding="utf-8")


def load_template() -> str:
    return TEMPLATE_FILE.read_text(encoding="utf-8")


def load_pages() -> dict[str, dict[str, Any]]:
    pages: dict[str, dict[str, Any]] = {}
    for file in sorted(PAGES_DIR.glob("*.json")):
        try:
            if file.stat().st_size > MAX_JSON_SIZE:
                print(f"Skipping oversized JSON file {file.name}")
                continue
            data = json.loads(file.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Skipping invalid JSON file {file.name}: {exc}")
            continue
        slug = str(data.get("slug") or file.stem).strip() or file.stem
        if not is_safe_slug(slug):
            print(f"Skipping unsafe slug in {file.name}: {slug!r}")
            continue
        if slug in pages:
            print(f"Skipping duplicate slug in {file.name}: {slug!r}")
            continue
        data["slug"] = slug
        data["_source_file"] = file.name
        pages[slug] = data
    return pages


def render_sections(page: dict[str, Any]) -> str:
    sections = page.get("sections", [])
    out: list[str] = []

    for section in sections:
        title = html.escape(str(section.get("title", "Untitled")))
        section_type = str(section.get("type", "table")).strip().lower()

        if section_type == "text":
            text = html.escape(str(section.get("text", ""))).replace("\n", "<br>")
            out.append(
                f"""
                <section class="card">
                  <div class="card-title">{title}</div>
                  <div class="content-block text-block">
                    {text}
                  </div>
                </section>
                """
            )
            continue


        if section_type == "table":
            items = section.get("items", [])
            rows: list[str] = []

            for item in items:
                if isinstance(item, dict):
                    key = html.escape(str(item.get("key", "")))
                    raw_value = str(item.get("value", ""))
                elif isinstance(item, list) and len(item) >= 2:
                    key = html.escape(str(item[0]))
                    raw_value = str(item[1])
                else:
                    key = ""
                    raw_value = str(item)

                if raw_value.startswith(("http://", "https://")):
                    value = (
                        f"<a href='{html.escape(raw_value)}' "
                        f"target='_blank' rel='noopener noreferrer' "
                        f"class='ext-link'>{html.escape(raw_value)}</a>"
                    )
                else:
                    value = html.escape(raw_value)

                rows.append(f"<tr><td class='k'>{key}</td><td class='v'>{value}</td></tr>")

            out.append(
                f"""
                <section class="card">
                  <div class="card-title">{title}</div>
                  <table class="mini-table">
                    {''.join(rows)}
                  </table>
                </section>
                """
            )
            continue


        if section_type == "code":
            language = html.escape(str(section.get("language", "text")).strip().lower())
            code = html.escape(str(section.get("code", "")))

            out.append(
                f"""
                <section class="card card-wide">
                  <div class="card-title">
                    {title} <span class="code-lang">{language}</span>
                  </div>
                  <pre class="code-block"><code class="language-{language}">{code}</code></pre>
                </section>
                """
            )
            continue

        # Optional fallback for unsupported section types
        out.append(
            f"""
            <section class="card">
              <div class="card-title">{title}</div>
              <div class="content-block text-block">
                Unsupported section type: {html.escape(section_type)}
              </div>
            </section>
            """
        )

    return "".join(out)


def render_ascii(page: dict[str, Any]) -> str:
    ascii_cfg = page.get("ascii")
    if not ascii_cfg:
        return ""

    blocks_across = int(ascii_cfg.get("blocks_across", 6))
    title = html.escape(str(ascii_cfg.get("title", "ASCII TABLE 1–255")))
    min_width = int(ascii_cfg.get("min_width_px", 920))

    start = 1
    end = 255
    total_values = end - start + 1

    rows_per_block = (total_values + blocks_across - 1) // blocks_across

    header = "".join("<th>Dec</th><th>Hex</th><th>Char</th>" for _ in range(blocks_across))
    rows = []

    for row_index in range(rows_per_block):
        tds = []

        for col_index in range(blocks_across):
            v = start + col_index * rows_per_block + row_index

            if v <= end:
                ch = chr(v) if 32 <= v <= 126 else "."
                tds.append(f"<td>{v}</td><td>Ox{v:02X}</td><td>{html.escape(ch)}</td>")
            else:
                tds.append("<td></td><td></td><td></td>")

        rows.append("<tr>" + "".join(tds) + "</tr>")

    return f"""
    <section class="ascii-wrap">
      <div class="ascii-title">{title}</div>
      <div class="mobile-note">On phones, swipe sideways to view the full table.</div>
      <div class="ascii-scroll">
        <table class="ascii-table" style="min-width:{min_width}px">
          <thead><tr>{header}</tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>
    </section>
    """


def render_nav(
    pages: dict[str, dict[str, Any]],
    current_slug: str | None = None,
    open_by_default: bool = False
) -> str:

    links = []

    # --- Always add HOME link first ---
    home_active = " active" if current_slug is None else ""
    links.append(f"<a class='nav-link{home_active}' href='/'>[ / ] ROOT DIRECTORY</a>")

    # --- Add all pages ---
    for slug, page in pages.items():
        title = html.escape(str(page.get("title", slug)))
        active = " active" if slug == current_slug else ""
        links.append(f"<a class='nav-link{active}' href='/{slug}'>{title}</a>")

    open_attr = " open" if open_by_default else ""

    return f"""
    <section class="nav-shell">
      <details class="nav-drawer"{open_attr}>
        <summary class="nav-summary">
          INDEX // {len(pages) + 1} PAGES // {'CURRENT: ' + html.escape(current_slug) if current_slug else 'HOME'}
        </summary>
        <div class="nav-list">
          {''.join(links)}
        </div>
      </details>
    </section>
    """


def render_home(pages: dict[str, dict[str, Any]], template: str) -> str:
    cards = []
    for slug, page in pages.items():
        title = html.escape(str(page.get("title", slug)))
        subtitle = html.escape(str(page.get("subtitle", "")))
        source = html.escape(str(page.get("_source_file", "")))
        cards.append(
            f"""
            <section class="card home-card">
              <div class="card-title">{title}</div>
              <div class="home-card-body">
                <p>{subtitle}</p>
                <p class="meta">Source: {source}</p>
                <a class="open-btn" href="/{slug}">Open page</a>
              </div>
            </section>
            """
        )
    return (
        template
        .replace("{{PAGE_TITLE}}", "LAN Reference Site")
        .replace("{{PAGE_SUBTITLE}}", "Edit JSON files in the pages folder and refresh.")
        .replace("{{TOP_BAR}}", "LAN Cheatsheet Host // Home")
        .replace("{{NAV_HTML}}", render_nav(pages, open_by_default=True))
        .replace("{{SECTIONS_HTML}}", "".join(cards))
        .replace("{{ASCII_HTML}}", "")
    )


def render_page(page: dict[str, Any], pages: dict[str, dict[str, Any]], template: str) -> str:
    title = html.escape(str(page.get("title", page["slug"])))
    subtitle = html.escape(str(page.get("subtitle", "")))
    sections_html = render_sections(page)
    ascii_html = render_ascii(page)
    return (
        template
        .replace("{{PAGE_TITLE}}", title)
        .replace("{{PAGE_SUBTITLE}}", subtitle)
        .replace("{{TOP_BAR}}", f"LAN Content Site // {title}")
        .replace("{{NAV_HTML}}", render_nav(pages, current_slug=page["slug"], open_by_default=False))
        .replace("{{SECTIONS_HTML}}", sections_html)
        .replace("{{ASCII_HTML}}", ascii_html)
    )


class ContentHandler(BaseHTTPRequestHandler):
    server_version = "ContentDrivenLanHost/1.0"

    def _send_bytes(self, data: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' https: data:; style-src 'self' 'unsafe-inline'; script-src 'none'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        )
        self.end_headers()
        self.wfile.write(data)


    def _send_html(self, html_text: str, status: int = 200) -> None:
        self._send_bytes(html_text.encode("utf-8"), "text/html; charset=utf-8", status)


    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        self._send_bytes(json.dumps(payload, indent=2).encode("utf-8"), "application/json; charset=utf-8", status)


    def do_GET(self) -> None:
        pages = load_pages()
        template = load_template()
        if self.path in ("/", "/index.html"):
            self._send_html(render_home(pages, template))
            return
        if self.path == "/api/pages":
            self._send_json({"pages": list(pages.keys())})
            return
        slug = self.path.lstrip("/").strip()
        if slug in pages:
            self._send_html(render_page(pages[slug], pages, template))
            return
        self._send_json({"error": "Not found"}, status=404)


    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {fmt % args}")



DEFAULT_TEMPLATE = ""

DEFAULT_PAGE = {
  "slug": "getting-started",
  "title": "Getting Started with Cheatsheets",
  "subtitle": "Learn how to create your own reference pages using JSON",
  "sections": [
    {
      "type": "text",
      "title": "How This Works",
      "text": "This is an automatically generated example page. When you add your own JSON files to the 'pages' folder, they will appear here instead. Each JSON file becomes a cheatsheet page with sections for organizing your content."
    },
    {
      "type": "table",
      "title": "Section Types Available",
      "items": [
        {"key": "text", "value": "Plain text content with line breaks"},
        {"key": "table", "value": "Key-value pairs in tabular format"},
        {"key": "code", "value": "Syntax-highlighted code blocks"},
        {"key": "ascii", "value": "Character reference tables (optional)"}
      ]
    },
    {
      "type": "table",
      "title": "Table Formats",
      "items": [
        ["Dictionary", '{"key": "Command", "value": "Description"}'],
        ["Array", '["key", "value"]'],
        ["Mixed", "Both formats work in the same table"]
      ]
    },
    {
      "type": "code",
      "title": "JSON Structure Example",
      "language": "json",
      "code": "{\n  \"slug\": \"my-cheatsheet\",\n  \"title\": \"My Reference Sheet\",\n  \"subtitle\": \"Brief description\",\n  \"sections\": [\n    {\n      \"type\": \"table\",\n      \"title\": \"Commands\",\n      \"items\": [\n        {\"key\": \"cmd\", \"value\": \"description\"}\n      ]\n    }\n  ]\n}"
    },
    {
      "type": "text",
      "title": "Next Steps",
      "text": "1. Create a new .json file in the pages/ folder\n2. Copy the structure shown above\n3. Add your own content\n4. Refresh your browser to see changes\n\nThe server automatically detects new files and updates the navigation."
    }
  ],
  "ascii": {
    "title": "ASCII Reference (1-127)",
    "blocks_across": 4,
    "min_width_px": 500
  }
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Host a content-driven LAN site from template + JSON files.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    ensure_defaults()
    server = ThreadingHTTPServer((args.host, args.port), ContentHandler)
    local_ip = get_local_ip()
    print()
    print("Content-driven LAN site is running.")
    print(f"Template file:    {TEMPLATE_FILE}")
    print(f"Pages folder:     {PAGES_DIR}")
    print(f"Local access:     http://127.0.0.1:{args.port}")
    print(f"Network access:   http://{local_ip}:{args.port}")
    print()
    print("Edit site_template.html to change layout/styling.")
    print("Edit or add JSON files in pages/ to add new landing pages.")
    print("Refresh the browser after saving changes.")
    print("Press Ctrl+C to stop.")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()



if __name__ == "__main__":
    main()
