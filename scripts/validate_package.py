"""Validate this review package offline using only the Python standard library.

This performs static checks, not notebook execution or MySQL query validation.
"""
import ast
import base64
import json
import os
from pathlib import Path
import re
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".gitignore", "README.md", "requirements.txt", "config.example.env",
    "sakila_analysis.ipynb", "sql/analysis.sql", "docs/schema.md",
    "docs/validation.md", "assets/films_by_rating.png", "scripts/validate_package.py",
}
QUERY_NAMES = [
    "films_by_rating", "distinct_films_in_stock", "films_unavailable",
    "store_cities", "top_actor_all_categories",
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_png(raw):
    require(raw.startswith(b"\x89PNG\r\n\x1a\n"), "Invalid chart PNG signature")
    pos = 8
    chunks = []
    while pos < len(raw):
        require(pos + 12 <= len(raw), "Truncated PNG")
        size = struct.unpack(">I", raw[pos:pos + 4])[0]
        kind = raw[pos + 4:pos + 8]
        end = pos + 12 + size
        require(end <= len(raw), "PNG chunk exceeds file")
        require(kind in {b"IHDR", b"PLTE", b"tRNS", b"IDAT", b"IEND"},
                "Unexpected PNG metadata chunk")
        require(zlib.crc32(raw[pos + 4:end - 4]) & 0xffffffff ==
                struct.unpack(">I", raw[end - 4:end])[0], "Invalid PNG checksum")
        chunks.append(kind)
        pos = end
    require(chunks[0] == b"IHDR" and chunks[-1] == b"IEND", "Incomplete chart PNG")
    require(b"IDAT" in chunks, "Missing PNG pixels")


def main():
    paths = []
    for directory, folders, names in os.walk(ROOT):
        folders[:] = [name for name in folders if name not in
                      {".git", ".venv", ".ipynb_checkpoints", "__pycache__"}]
        for name in names:
            if name == ".DS_Store" or name == ".env" or name.startswith(".env.") or name.endswith(".local.env"):
                continue
            paths.append(Path(directory) / name)
    actual = {p.relative_to(ROOT).as_posix() for p in paths}
    require(actual == EXPECTED, "Unexpected or missing package files")
    require(not any(p.is_symlink() for p in paths), "Package contains a symlink")

    # Check text files and decoded notebook output separately from base64 image data.
    nb = json.loads((ROOT / "sakila_analysis.ipynb").read_text())
    require(nb.get("nbformat") == 4 and nb.get("nbformat_minor") == 5,
            "Expected notebook format 4.5")
    require(set(nb) == {"cells", "metadata", "nbformat", "nbformat_minor"},
            "Unexpected top-level notebook metadata")
    require(set(nb["metadata"]) == {"kernelspec", "language_info"},
            "Unexpected notebook metadata")
    require(isinstance(nb["cells"], list) and nb["cells"], "Notebook has no cells")
    ids = set()
    python_cells = 0
    saved_outputs = 0
    query_strings = {}
    prose_and_code = []
    chart = (ROOT / "assets/films_by_rating.png").read_bytes()
    check_png(chart)
    embedded_charts = 0
    for cell in nb["cells"]:
        require(cell["cell_type"] in {"markdown", "code"}, "Unexpected notebook cell type")
        require(cell.get("metadata") == {}, "Unexpected cell metadata")
        cell_id = cell.get("id", "")
        require(re.fullmatch(r"[A-Za-z0-9_-]{1,64}", cell_id) and cell_id not in ids,
                "Invalid or duplicate cell ID")
        ids.add(cell_id)
        require(isinstance(cell["source"], list) and
                all(isinstance(line, str) for line in cell["source"]), "Invalid cell source")
        source = "".join(cell["source"])
        prose_and_code.append(source)
        if cell["cell_type"] == "markdown":
            require(set(cell) == {"id", "metadata", "source", "cell_type"},
                    "Unexpected markdown cell fields")
            continue
        require(set(cell) == {"id", "metadata", "source", "cell_type", "outputs", "execution_count"},
                "Unexpected code cell fields")
        require(cell["execution_count"] is None, "Execution count must be cleared")
        tree = ast.parse(source)
        compile(tree, "<notebook-cell>", "exec")
        python_cells += 1
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        require(not (re.search(r"password|passwd|secret|token", target.id, re.I)
                                     and isinstance(node.value.value, str) and node.value.value),
                                "Literal credential assignment")
                        if target.id.endswith("_sql"):
                            query_strings[target.id[:-4]] = node.value.value.strip()
            if isinstance(node, ast.Call):
                for keyword in node.keywords:
                    if keyword.arg and re.search(r"password|passwd|secret|token", keyword.arg, re.I):
                        require(not (isinstance(keyword.value, ast.Constant) and keyword.value.value),
                                "Literal credential argument")
        for output in cell["outputs"]:
            require(set(output) == {"data", "metadata", "output_type"}, "Unexpected output fields")
            require(output["output_type"] == "display_data" and output["metadata"] == {},
                    "Unexpected saved output metadata")
            require(set(output["data"]) <= {"text/plain", "text/html", "image/png"},
                    "Unexpected saved MIME type")
            saved_outputs += 1
            for mime, data in output["data"].items():
                require(isinstance(data, (str, list)), "Invalid MIME payload")
                value = "".join(data) if isinstance(data, list) else data
                if mime == "image/png":
                    decoded = base64.b64decode(value, validate=True)
                    require(decoded == chart, "Embedded chart differs from reviewed asset")
                    embedded_charts += 1
                else:
                    prose_and_code.append(value)
                    require(not re.search(r"<script\b|\son\w+\s*=|javascript:", value, re.I),
                            "Active content in saved output")
    require(embedded_charts == 1 and saved_outputs == 7, "Expected six result tables and one chart")
    require(list(query_strings) == QUERY_NAMES, "Expected five analytical queries")

    sql_file = (ROOT / "sql/analysis.sql").read_text()
    standalone = {}
    for block in re.split(r"^-- query: ", sql_file, flags=re.M)[1:]:
        name, body = block.split("\n", 1)
        statement = "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("--")).strip()
        require(statement.upper().startswith("SELECT ") and statement.count(";") == 1
                and statement.endswith(";"), "Expected one SELECT statement per query")
        require(not re.search(r"\b(?:INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|GRANT|CALL|OUTFILE|DUMPFILE)\b",
                              statement, re.I), "Unexpected mutating SQL keyword")
        standalone[name] = statement
    require(standalone == query_strings, "Notebook and standalone SQL differ")

    for rel in sorted(EXPECTED):
        path = ROOT / rel
        if path.suffix == ".py":
            compile(path.read_text(), rel, "exec")
        if path.suffix != ".png" and path.suffix != ".ipynb":
            prose_and_code.append(path.read_text())
    # Patterns are assembled to avoid flagging the validator's own pattern definitions.
    checks = ["/" + r"Users/[^\s]+", "/" + r"var/folders/[^\s]+", r"[A-Za-z]:\\Users\\[^\s]+",
              r"\b" + "hf_" + r"[A-Za-z0-9]{15,}",
              r"\b" + "sk-" + r"[A-Za-z0-9_-]{20,}",
              r"\b" + "AKIA" + r"[A-Z0-9]{16}",
              "-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
              r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"]
    for content in prose_and_code:
        for pattern in checks:
            require(not re.search(pattern, content), "Potential secret or private path; inspect locally")

    # Keep relative Markdown targets reviewable without relying on network access.
    for rel in ["README.md", "docs/schema.md", "docs/validation.md"]:
        for target in re.findall(r"\]\(([^)]+)\)", (ROOT / rel).read_text()):
            if not target.startswith(("https://", "http://", "#")):
                require((ROOT / rel).parent.joinpath(target).is_file(), "Broken relative document link")
    print(f"PASS: {len(EXPECTED)} files; notebook 4.5 structure; {python_cells} Python cells compile;")
    print("      five matching read-only SQL queries; six saved tables and one chart;")
    print("      metadata allowlists, PNG checks, private-path/token patterns, and local links.")
    print("Static checks only. No notebook execution, dependency installation, or database connection.")


if __name__ == "__main__":
    main()
