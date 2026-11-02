"""Static file and docs-discovery routes, including the catch-all.

This blueprint owns ``/<path:path>`` and is registered LAST in
``webapp.routes.ALL_BLUEPRINTS`` so concrete routes always win.
"""

from html import escape
from pathlib import Path

from flask import Blueprint, Response, jsonify, request, send_from_directory

from webapp import REPO_ROOT

bp = Blueprint("static_docs", __name__)


@bp.route("/")
def index():
    return send_from_directory(str(REPO_ROOT / "frontend"), "index.html")


def render_markdown_doc(markdown_path: Path):
    """Render repository markdown docs as simple crawlable HTML aliases."""
    source = markdown_path.read_text(encoding="utf-8")
    title = markdown_path.stem.replace("-", " ").title()
    body = []
    in_list = False
    in_code = False
    code_lines = []

    def close_list():
        nonlocal in_list
        if in_list:
            body.append("</ul>")
            in_list = False

    for raw_line in source.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            if in_code:
                body.append(
                    f"<pre><code>{escape(chr(10).join(code_lines))}</code></pre>"
                )
                code_lines = []
                in_code = False
            else:
                close_list()
                in_code = True
            continue
        if in_code:
            code_lines.append(raw_line)
            continue
        if not line:
            close_list()
            continue
        if line.startswith("#"):
            close_list()
            level = min(len(line) - len(line.lstrip("#")), 6)
            text = line[level:].strip()
            if level == 1:
                title = text
            body.append(f"<h{level}>{escape(text)}</h{level}>")
            continue
        if line.startswith(("- ", "* ")):
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{escape(line[2:])}</li>")
            continue
        close_list()
        body.append(f"<p>{escape(line)}</p>")

    close_list()
    if in_code:
        body.append(f"<pre><code>{escape(chr(10).join(code_lines))}</code></pre>")

    canonical = f"https://kyanitelabs.github.io/openglaze/{markdown_path.stem}.html"
    html = "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(title)} | OpenGlaze</title>",
            f'<link rel="canonical" href="{canonical}">',
            "</head>",
            "<body>",
            "<main>",
            *body,
            "</main>",
            "</body>",
            "</html>",
        ]
    )
    return Response(html, mimetype="text/html")


@bp.route("/llms.txt")
@bp.route("/llms-full.txt")
@bp.route("/ai.txt")
@bp.route("/robots.txt")
@bp.route("/sitemap.xml")
@bp.route("/social-preview.png")
def docs_root_asset():
    return send_from_directory(str(REPO_ROOT / "docs"), request.path.lstrip("/"))


@bp.route("/<path:path>")
def static_files(path):
    # Don't serve hidden files or paths outside public static/docs directories
    if path.startswith(".") or ".." in path:
        return jsonify({"error": "Not found"}), 404
    if path.endswith((".html", ".txt", ".xml", ".png")):
        docs_file = REPO_ROOT / "docs" / path
        if docs_file.is_file():
            return send_from_directory(str(REPO_ROOT / "docs"), path)
        if path.endswith(".html"):
            markdown_file = REPO_ROOT / "docs" / f"{Path(path).stem}.md"
            if markdown_file.is_file():
                return render_markdown_doc(markdown_file)
    response = send_from_directory(str(REPO_ROOT / "frontend"), path)
    if path == "sw.js":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response
