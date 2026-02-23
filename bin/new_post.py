#!/usr/bin/env python3
"""
Create a new Hugo blog post interactively.

Usage:
    python bin/new_post.py

Supported post types: post, recipe, review (game / film / book / other)
"""

import re
import sys
import time
import pathlib
import textwrap
from datetime import datetime, timezone


# ── Slug ─────────────────────────────────────────────────────────────────────

def slugify(title: str) -> str:
    """Convert a title to a URL-safe slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')


# ── Frontmatter builder ───────────────────────────────────────────────────────

def render_frontmatter(
    title: str,
    draft: bool,
    date: str,
    extra_params: dict,
    tags: list[str],
) -> str:
    lines = ["---"]
    lines.append(f'title: "{title}"')
    lines.append("params:")
    lines.append("  nav: blog")
    for key, val in extra_params.items():
        v = "true" if val is True else "false" if val is False else str(val)
        lines.append(f"  {key}: {v}")
    lines.append(f"draft: {'true' if draft else 'false'}")
    lines.append(f"date: {date}")
    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {tag.strip()}")
    lines.append("---")
    return "\n".join(lines)


# ── Content templates ─────────────────────────────────────────────────────────

def render_post(title: str, draft: bool, date: str, tags: list[str]) -> str:
    fm = render_frontmatter(title, draft, date, {}, tags)
    return fm + "\n\n"


def render_recipe(title: str, draft: bool, date: str, tags: list[str]) -> str:
    fm = render_frontmatter(title, draft, date, {"recipe": True}, tags)
    body = textwrap.dedent("""\

        {{< recipe-meta prep="" cook="" serves="" difficulty="" >}}

        ## Ingredients

        {{< ingredients serves="" >}}
          {{< ingredient-group name="" >}}
            {{< ingredient qty="" unit="" >}}{{< /ingredient >}}
          {{< /ingredient-group >}}
        {{< /ingredients >}}

        ## Method

        1.
    """)
    return fm + body


def render_review(
    title: str,
    subtype: str,
    draft: bool,
    date: str,
    tags: list[str],
) -> str:
    fm = render_frontmatter(title, draft, date, {"review": True}, tags)

    meta_fields = {
        "game":  'genre="" year="" developer="" platform="" players=""',
        "film":  'genre="" year="" director="" studio="" duration=""',
        "book":  'genre="" year=""',
        "other": 'genre="" year=""',
    }
    meta_attr = meta_fields.get(subtype, meta_fields["other"])

    body = textwrap.dedent(f"""\

        {{{{< review-meta {meta_attr} >}}}}

        {{{{< review-score score="" max="10" label="" >}}}}

        ## Overview

        {{{{< pros-cons pros="Pro 1|Pro 2" cons="Con 1|Con 2" >}}}}

        {{{{< verdict verdict="" >}}}}
        Your verdict here.
        {{{{< /verdict >}}}}
    """)
    return fm + body


# ── File system ───────────────────────────────────────────────────────────────

def create_post_dir(content_blog_path: pathlib.Path, ts: int, slug: str) -> pathlib.Path:
    """Create and return the post directory."""
    post_dir = content_blog_path / f"{ts}_{slug}"
    post_dir.mkdir(parents=True, exist_ok=True)
    return post_dir
