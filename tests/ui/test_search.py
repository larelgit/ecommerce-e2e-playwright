"""Product search: the happy path and the empty-result case."""

import pytest
from playwright.sync_api import Page, expect

from pages.product_page import ProductPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
def test_search_finds_matching_products(page: Page) -> None:
    products = ProductPage(page)
    products.open()
    products.search("dress")

    expect(products.search_results_heading).to_be_visible()
    names = products.product_names()
    assert names, "search for a common term returned no products"
    # Search has returned names without "dress" (see README field notes).
    # Name-only matching is not a documented contract; the matching fields
    # and the relevance requirement still need confirmation from the owner.
    assert any("dress" in name.lower() for name in names), names


def test_search_with_no_matches_shows_empty_grid(page: Page) -> None:
    products = ProductPage(page)
    products.open()
    products.search("definitely-not-a-product-9000")

    expect(products.search_results_heading).to_be_visible()
    expect(products.product_cards).to_have_count(0)
