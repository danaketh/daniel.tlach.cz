#!/usr/bin/env python3
"""
Generate a food photograph for a Hugo recipe post using DALL-E 3.

Usage:
    python bin/generate_recipe_image.py content/blog/2026-02-19_texas-chilli/

The script:
  1. Reads index.en.md (falls back to the first index.*.md found)
  2. Extracts the recipe title and key ingredients
  3. Builds a food-photography prompt
  4. Calls the OpenAI Images API (DALL-E 3)
  5. Saves cover.jpg into the recipe directory
  6. Patches the thumbnail front matter field in ALL language variants

Requires:
    pip install -r requirements.txt
    OPENAI_API_KEY environment variable (or .env file)
"""

import os
import re
import sys
import pathlib
import textwrap

import base64

import frontmatter
from openai import OpenAI
from dotenv import load_dotenv

# ── Configuration ────────────────────────────────────────────────────────────

IMAGE_FILENAME = "cover.jpg"
IMAGE_SIZE     = "1536x1024"   # landscape, good for hero / thumbnail
IMAGE_QUALITY  = "high"        # "low" | "medium" | "high"


# ── Prompt builder ───────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = textwrap.dedent("""\
    {prompt}
""")

def build_prompt(prompt: str) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(prompt=prompt)


# ── Hugo front matter helpers ─────────────────────────────────────────────────

def load_post(path: pathlib.Path):
    return frontmatter.load(str(path))


def save_post(post, path: pathlib.Path):
    with open(path, "wb") as f:
        frontmatter.dump(post, f)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def patch_post_meta(md_path: pathlib.Path, slug: str, thumbnail_value: str):
    post = load_post(md_path)
    post["slug"] = slug
    post["thumbnail"] = thumbnail_value
    save_post(post, md_path)
    print(f"  patched slug + thumbnail in {md_path.name}")


# ── Image generation ─────────────────────────────────────────────────────────

def generate_image(prompt: str, out_path: pathlib.Path):
    client = OpenAI()  # reads OPENAI_API_KEY from environment

    print("Sending request to OpenAI …")
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=IMAGE_SIZE,
        quality=IMAGE_QUALITY,
        n=1,
    )

    img_b64 = response.data[0].b64_json
    print(f"Saving → {out_path} …")
    img_data = base64.b64decode(img_b64)
    out_path.write_bytes(img_data)
    print(f"Saved {len(img_data) // 1024} KB")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    load_dotenv()

    recipe_dir = pathlib.Path(sys.argv[1]).resolve()
    if not recipe_dir.is_dir():
        print(f"Error: {recipe_dir} is not a directory")
        sys.exit(1)

    # Find English source; fall back to any index.*.md
    en_file = recipe_dir / "index.en.md"
    if not en_file.exists():
        candidates = sorted(recipe_dir.glob("index.*.md"))
        if not candidates:
            print(f"Error: no index.*.md found in {recipe_dir}")
            sys.exit(1)
        en_file = candidates[0]

    print(f"Reading: {en_file}")
    post        = load_post(en_file)
    title       = post.get("title", recipe_dir.name)
    cover_prompt = post.get("cover_prompt")
    print(f"Title      : {title}")
    prompt = build_prompt(cover_prompt)
    print(f"\nPrompt:\n{prompt}")

    cover_path = recipe_dir / IMAGE_FILENAME
    generate_image(prompt, cover_path)

    # Derive slug and thumbnail path matching the Hugo permalink format:
    # /blog/YYYY-MM-DD-{slug}/cover.jpg
    date_val = post.get("date")
    date_str = date_val.strftime("%Y-%m-%d") if hasattr(date_val, "strftime") else str(date_val)[:10]
    slug = slugify(title)
    thumbnail_value = f"/blog/{date_str}-{slug}/{IMAGE_FILENAME}"

    print(f"\nSlug           : {slug}")
    print(f"Thumbnail path : {thumbnail_value}")

    # Patch all language variants
    for md_file in sorted(recipe_dir.glob("index.*.md")):
        patch_post_meta(md_file, slug, thumbnail_value)

    print("\nDone.")


if __name__ == "__main__":
    main()
