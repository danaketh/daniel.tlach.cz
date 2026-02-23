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


# ── Prompts ───────────────────────────────────────────────────────────────────

def prompt(question: str, options: list[str] | None = None, default: str = "") -> str:
    """Print a prompt and return the user's answer."""
    if options:
        opts_str = " / ".join(
            f"[{o}]" if o == default else o for o in options
        )
        question = f"{question} ({opts_str})"
    elif default:
        question = f"{question} [{default}]"
    while True:
        answer = input(f"  {question}: ").strip()
        if not answer and default:
            return default
        if answer:
            if options and answer not in options:
                print(f"    Please enter one of: {', '.join(options)}")
                continue
            return answer
        if not options and not default:
            # Free-form field, empty is OK
            return answer


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Locate content/blog relative to this script (bin/../content/blog)
    script_dir = pathlib.Path(__file__).resolve().parent
    content_blog = script_dir.parent / "content" / "blog"
    if not content_blog.is_dir():
        print(f"Error: {content_blog} does not exist. Run from project root.")
        sys.exit(1)

    print("\n=== New Hugo Post ===\n")

    # 1. Post type
    post_type = prompt("Post type", options=["post", "recipe", "review"])

    # 2. Review sub-type
    review_subtype = None
    if post_type == "review":
        review_subtype = prompt("Review sub-type", options=["game", "film", "book", "other"])

    # 3. Title → slug
    while True:
        title = input("  Title: ").strip()
        if title:
            break
        print("    Title cannot be empty.")

    slug = slugify(title)
    print(f"  Slug: {slug}")

    # 4. Tags
    raw_tags = input("  Tags (comma-separated, or Enter to skip): ").strip()
    tags = [t.strip() for t in raw_tags.split(",") if t.strip()] if raw_tags else []

    # 5. Languages
    lang_choice = prompt("Language(s)", options=["en", "cs", "both"], default="en")
    languages = ["en", "cs"] if lang_choice == "both" else [lang_choice]

    # 6. Draft
    draft_choice = prompt("Draft?", options=["yes", "no"], default="yes")
    draft = draft_choice == "yes"

    # Build timestamp + ISO date
    ts = int(time.time())
    now = datetime.now(tz=timezone.utc).astimezone()
    iso_date = now.isoformat()

    # Render content
    if post_type == "post":
        content = render_post(title, draft, iso_date, tags)
    elif post_type == "recipe":
        content = render_recipe(title, draft, iso_date, tags)
    else:
        content = render_review(title, review_subtype, draft, iso_date, tags)

    # Create directory and files
    post_dir = create_post_dir(content_blog, ts, slug)
    created = []
    for lang in languages:
        file_path = post_dir / f"index.{lang}.md"
        file_path.write_text(content, encoding="utf-8")
        created.append(file_path)

    print(f"\nCreated: {post_dir}")
    for f in created:
        print(f"  {f.relative_to(script_dir.parent)}")

    if post_type == "recipe":
        print(
            f"\nTip: Once you've written the recipe, generate a cover image with:\n"
            f"  python bin/generate_recipe_image.py {post_dir.relative_to(script_dir.parent)}"
        )

    print()


if __name__ == "__main__":
    main()
