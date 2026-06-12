from playwright.sync_api import Page

from pages.base_page import BasePage


class ProductPage(BasePage):
    """Catalog (/products): search, product grid, details view, add-to-cart modal."""

    path = "/products"

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = page.get_by_placeholder("Search Product")
        self.search_button = page.locator("#submit_search")
        self.search_results_heading = page.get_by_role(
            "heading", name="Searched Products"
        )
        self.product_cards = page.locator(".features_items .product-image-wrapper")

    def search(self, query: str) -> None:
        self.search_input.fill(query)
        self.search_button.click()

    def product_names(self) -> list[str]:
        return self.product_cards.locator(".productinfo p").all_inner_texts()

    def add_to_cart(self, index: int = 0) -> str:
        """Adds the n-th product from the grid and returns its name."""
        card = self.product_cards.nth(index)
        name = card.locator(".productinfo p").inner_text()
        card.locator(".productinfo .add-to-cart").click()
        return name

    def continue_shopping(self) -> None:
        self.page.get_by_role("button", name="Continue Shopping").click()

    def go_to_cart_from_modal(self) -> None:
        self.page.get_by_role("link", name="View Cart").click()

    # --- product details view ---

    def open_details(self, index: int = 0) -> None:
        self.product_cards.nth(index).get_by_role("link", name="View Product").click()

    def details_price(self) -> int:
        return self.parse_price(
            self.page.locator(".product-information span span").inner_text()
        )

    def set_quantity(self, quantity: int) -> None:
        self.page.locator("#quantity").fill(str(quantity))

    def add_to_cart_from_details(self) -> None:
        self.page.get_by_role("button", name="Add to cart").click()
