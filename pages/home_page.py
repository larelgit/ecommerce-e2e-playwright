from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class HomePage(BasePage):
    path = "/"

    def __init__(self, page: Page):
        super().__init__(page)
        self.featured_items: Locator = page.locator(
            ".features_items .product-image-wrapper"
        )
