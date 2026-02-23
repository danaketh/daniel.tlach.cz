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

import requests
import frontmatter
from openai import OpenAI

# ── Configuration ────────────────────────────────────────────────────────────

IMAGE_FILENAME = "cover.jpg"
IMAGE_SIZE     = "1792x1024"   # landscape, good for hero / thumbnail
IMAGE_QUALITY  = "hd"          # "standard" is cheaper; "hd" is sharper
IMAGE_STYLE    = "natural"     # "vivid" for dramatic, "natural" for realistic


# ── Prompt builder ───────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = textwrap.dedent("""\
    Professional food photography of {title}.
    Hero ingredients visible: {ingredients}.
    Shot style: overhead or 45-degree angle, dark moody background,
    natural side-lighting, shallow depth of field, rustic tableware,
    garnished and styled for a food magazine cover.
    No text, no watermarks, photorealistic, high resolution.
""")

def extract_ingredients(text: str) -> list[str]:
    """Pull ingredient names from Hugo shortcode content."""
    # Match {{< ingredient qty="…" unit="…" >}}NAME{{< /ingredient >}}
    # The ingredient name is the inner text (strip surrounding whitespace).
    pattern = r'\{\{<\s*ingredient[^>]*>\}\}(.*?)\{\{<\s*/ingredient\s*>\}\}'
    matches = re.findall(pattern, text, re.DOTALL)
    names = []
    for m in matches:
        name = m.strip()
        # Keep only the main part before parentheses / commas for brevity
        name = re.split(r'[,(]', name)[0].strip()
        if name and name not in names:
            names.append(name)
    return names


def build_prompt(title: str, ingredients: list[str]) -> str:
    top = ingredients[:8]  # don't overcrowd the prompt
    ing_str = ", ".join(top) if top else "the key ingredients"
    return SYSTEM_PROMPT_TEMPLATE.format(title=title, ingredients=ing_str)


# ── Hugo front matter helpers ─────────────────────────────────────────────────

def load_post(path: pathlib.Path):
    return frontmatter.load(str(path))


def save_post(post, path: pathlib.Path):
    with open(path, "wb") as f:
        frontmatter.dump(post, f)


def patch_thumbnail(md_path: pathlib.Path, thumbnail_value: str):
    post = load_post(md_path)
    post["thumbnail"] = thumbnail_value
    save_post(post, md_path)
    print(f"  patched thumbnail in {md_path.name}")


# ── Image generation ─────────────────────────────────────────────────────────

def generate_image(prompt: str, out_path: pathlib.Path):
    client = OpenAI()  # reads OPENAI_API_KEY from environment

    print("Sending request to DALL-E 3 …")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=IMAGE_SIZE,
        quality=IMAGE_QUALITY,
        style=IMAGE_STYLE,
        n=1,
    )

    image_url = response.data[0].url
    print(f"Image URL: {image_url}")

    print(f"Downloading → {out_path} …")
    img_data = requests.get(image_url, timeout=60).content
    out_path.write_bytes(img_data)
    print(f"Saved {len(img_data) // 1024} KB")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

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
    ingredients = extract_ingredients(post.content)

    print(f"Title      : {title}")
    print(f"Ingredients: {ingredients[:8]}")

    prompt = build_prompt(title, ingredients)
    print(f"\nPrompt:\n{prompt}")

    cover_path = recipe_dir / IMAGE_FILENAME
    generate_image(prompt, cover_path)

    # Hugo page-bundle path relative to content root: /blog/YYYY-slug/cover.jpg
    # We derive it by finding the "content" ancestor directory.
    try:
        content_root = next(
            p for p in recipe_dir.parents if p.name == "content"
        )
        rel = cover_path.relative_to(content_root)
        thumbnail_value = "/" + rel.as_posix()
    except StopIteration:
        # Fallback: just use the filename
        thumbnail_value = f"/{IMAGE_FILENAME}"

    print(f"\nThumbnail path: {thumbnail_value}")

    # Patch all language variants
    for md_file in sorted(recipe_dir.glob("index.*.md")):
        patch_thumbnail(md_file, thumbnail_value)

    print("\nDone.")


if __name__ == "__main__":
    main()
