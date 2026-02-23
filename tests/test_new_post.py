import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "bin"))
from new_post import slugify

def test_slugify_basic():
    assert slugify("Texas Chilli") == "texas-chilli"

def test_slugify_special_chars():
    assert slugify("Häagen-Dazs & Cream!") == "h-agen-dazs-cream"

def test_slugify_multiple_spaces():
    assert slugify("  hello   world  ") == "hello-world"

def test_slugify_leading_trailing_hyphens():
    assert slugify("--foo bar--") == "foo-bar"

def test_slugify_empty():
    assert slugify("") == ""

from new_post import render_frontmatter, render_post, render_recipe, render_review

def test_render_frontmatter_no_tags():
    fm = render_frontmatter(
        title="My Post",
        draft=True,
        date="2026-02-23T10:00:00+00:00",
        extra_params={},
        tags=[],
    )
    assert 'title: "My Post"' in fm
    assert "draft: true" in fm
    assert "tags:" not in fm

def test_render_frontmatter_with_tags():
    fm = render_frontmatter(
        title="My Post",
        draft=False,
        date="2026-02-23T10:00:00+00:00",
        extra_params={"recipe": True},
        tags=["food", "tex-mex"],
    )
    assert "draft: false" in fm
    assert "recipe: true" in fm
    assert "tags:" in fm
    assert "- food" in fm

def test_render_post_contains_frontmatter():
    content = render_post(
        title="Hello World", draft=True,
        date="2026-02-23T10:00:00+00:00", tags=[]
    )
    assert "nav: blog" in content

def test_render_recipe_has_shortcodes():
    content = render_recipe(
        title="Tacos", draft=True,
        date="2026-02-23T10:00:00+00:00", tags=[]
    )
    assert "recipe-meta" in content
    assert "ingredients" in content
    assert "ingredient-group" in content

def test_render_review_game_has_developer():
    content = render_review(
        title="Elden Ring", subtype="game", draft=True,
        date="2026-02-23T10:00:00+00:00", tags=[]
    )
    assert "developer=" in content
    assert "platform=" in content

def test_render_review_film_has_director():
    content = render_review(
        title="Dune", subtype="film", draft=True,
        date="2026-02-23T10:00:00+00:00", tags=[]
    )
    assert "director=" in content
    assert "duration=" in content

def test_render_review_book_minimal():
    content = render_review(
        title="Dune", subtype="book", draft=True,
        date="2026-02-23T10:00:00+00:00", tags=[]
    )
    assert "review-score" in content
    assert "verdict" in content
