#!/usr/bin/env python3
"""
Generate LaTeX experience files for the resume from YAML job data.

Usage:
    python bin/prepare_resume.py

Reads all .yaml files from data/jobs/ (sorted descending by filename) and writes:
  resume/experience.tex       — jobs with resume: true only
  resume/experience_full.tex  — all jobs

Requires:
    pip install -r requirements.txt
"""

import re
import sys
import pathlib

import yaml


# ── LaTeX helpers ─────────────────────────────────────────────────────────────

# Order matters: backslash must come first so later replacements don't
# double-escape the backslashes they introduce.
_LATEX_REPLACEMENTS = [
    ("\\", r"\textbackslash{}"),
    ("&",  r"\&"),
    ("%",  r"\%"),
    ("$",  r"\$"),
    ("#",  r"\#"),
    ("_",  r"\_"),
    ("{",  r"\{"),
    ("}",  r"\}"),
    ("~",  r"\textasciitilde{}"),
    ("^",  r"\textasciicircum{}"),
]

_MD_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def escape_latex(s: str) -> str:
    """Escape LaTeX special characters in s."""
    for old, new in _LATEX_REPLACEMENTS:
        s = s.replace(old, new)
    return s


def convert_markdown_links_to_latex(s: str) -> str:
    """Convert Markdown [text](url) links to LaTeX \\href{url}{text},
    escaping all other LaTeX special characters in the surrounding text."""
    parts = []
    last = 0
    for m in _MD_LINK_RE.finditer(s):
        if m.start() > last:
            parts.append(escape_latex(s[last:m.start()]))
        text, url = m.group(1), m.group(2)
        parts.append(rf"\href{{{url}}}{{{escape_latex(text)}}}")
        last = m.end()
    if last < len(s):
        parts.append(escape_latex(s[last:]))
    return "".join(parts)


def format_date(dt) -> str:
    """Format a date as M/YYYY with no leading zero on the month."""
    return f"{dt.month}/{dt.year}"


# ── YAML loading ──────────────────────────────────────────────────────────────

def load_jobs(jobs_dir: pathlib.Path) -> list[dict]:
    """Load all .yaml files from jobs_dir, sorted descending by filename."""
    files = sorted(
        [f for f in jobs_dir.iterdir() if f.suffix == ".yaml"],
        key=lambda f: f.name,
        reverse=True,
    )
    jobs = []
    for path in files:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data:
                jobs.append(data)
        except yaml.YAMLError as e:
            print(f"Warning: failed to parse {path.name}: {e}", file=sys.stderr)
    return jobs


# ── LaTeX generation ──────────────────────────────────────────────────────────

def generate_experience(jobs: list[dict], *, resume_only: bool) -> str:
    """Render jobs as a sequence of \\entry blocks for a LaTeX resume."""
    lines = []
    for job in jobs:
        if resume_only and not job.get("resume", False):
            continue

        date_range = job.get("range") or {}
        start = date_range.get("start")
        end = date_range.get("end")
        current = date_range.get("current", False)

        end_display = "Present" if current else format_date(end)
        start_display = format_date(start)

        title = (job.get("title") or "").strip()
        company = (job.get("company") or "").strip()
        description = convert_markdown_links_to_latex((job.get("description") or "").strip())
        technologies = job.get("technologies") or []

        lines.append("\\entry")
        lines.append(f"    {{{start_display} - {end_display}}}")
        lines.append(f"    {{{title}}}")
        lines.append(f"    {{{company}}}")

        if technologies:
            tech_str = "\\slashsep".join(
                f"\\texttt{{{escape_latex(t)}}}" for t in technologies
            )
            lines.append(f"    {{{description}\\\\ {tech_str}}}")
        else:
            lines.append(f"    {{{description}}}")

    return "\n".join(lines) + "\n"


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    root = pathlib.Path(__file__).resolve().parent.parent

    jobs_dir = root / "data" / "jobs"
    if not jobs_dir.is_dir():
        print(f"Error: {jobs_dir} does not exist.", file=sys.stderr)
        sys.exit(1)

    resume_dir = root / "resume"
    if not resume_dir.is_dir():
        print(f"Error: {resume_dir} does not exist.", file=sys.stderr)
        sys.exit(1)

    jobs = load_jobs(jobs_dir)

    (resume_dir / "experience.tex").write_text(
        generate_experience(jobs, resume_only=True), encoding="utf-8"
    )
    (resume_dir / "experience_full.tex").write_text(
        generate_experience(jobs, resume_only=False), encoding="utf-8"
    )

    print("LaTeX files generated successfully!")


if __name__ == "__main__":
    main()
