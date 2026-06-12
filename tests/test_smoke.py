"""Smoke check: the app is up and serves the home page."""
from playwright.sync_api import Page, expect


def test_home_page_opens(page: Page):
    page.goto("/")
    expect(page).to_have_title("Automation Exercise")
