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
