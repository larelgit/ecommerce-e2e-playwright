"""Smoke check: the app is up and serves the home page."""

import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
def test_home_page_opens(page: Page) -> None:
    home = HomePage(page)
    home.open()
    expect(page).to_have_title("Automation Exercise")
    expect(home.featured_items.first).to_be_visible()
