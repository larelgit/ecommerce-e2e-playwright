from playwright.sync_api import Page

from pages.base_page import BasePage


class CartPage(BasePage):
    path = "/view_cart"

    def __init__(self, page: Page):
        super().__init__(page)
        self.rows = page.locator("#cart_info_table tbody tr")
        self.empty_cart_message = page.get_by_text("Cart is empty!")
        self.checkout_login_prompt = page.get_by_text(
            "Register / Login account to proceed on checkout."
        )

    def item_names(self) -> list[str]:
        return self.rows.locator(".cart_description h4").all_inner_texts()

    def item_quantity(self, index: int = 0) -> int:
        return int(self.rows.nth(index).locator(".cart_quantity button").inner_text())

    def item_unit_price(self, index: int = 0) -> int:
        return self.parse_price(
            self.rows.nth(index).locator(".cart_price p").inner_text()
        )

    def item_total(self, index: int = 0) -> int:
        return self.parse_price(
            self.rows.nth(index).locator(".cart_total_price").inner_text()
        )

    def remove_item(self, index: int = 0) -> None:
        self.rows.nth(index).locator(".cart_quantity_delete").click()

    def proceed_to_checkout(self) -> None:
        self.page.get_by_text("Proceed To Checkout").click()
