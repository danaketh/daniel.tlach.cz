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
