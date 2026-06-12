"""Product search: the happy path and the empty-result case."""
from playwright.sync_api import Page, expect

from pages.product_page import ProductPage


def test_search_finds_matching_products(page: Page):
    products = ProductPage(page)
    products.open()
    products.search("dress")

    expect(products.search_results_heading).to_be_visible()
    names = products.product_names()
    assert names, "search for a common term returned no products"
    # A strict all() check here exposed a real quirk: the engine also matches
    # fields hidden from the results card (category/description), e.g. "dress"
    # returns "Sleeves Top and Short". Documented in README "Field notes".
    assert any("dress" in name.lower() for name in names), names


def test_search_with_no_matches_shows_empty_grid(page: Page):
    products = ProductPage(page)
    products.open()
    products.search("definitely-not-a-product-9000")

    expect(products.search_results_heading).to_be_visible()
    expect(products.product_cards).to_have_count(0)
