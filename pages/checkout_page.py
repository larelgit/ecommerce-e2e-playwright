from playwright.sync_api import Page

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    path = "/checkout"

    def __init__(self, page: Page):
        super().__init__(page)
        self.address_details_heading = page.get_by_role(
            "heading", name="Address Details"
        )
        self.review_order_heading = page.get_by_role(
            "heading", name="Review Your Order"
        )
        self.delivery_address = page.locator("#address_delivery")

    def add_order_comment(self, text: str) -> None:
        self.page.locator('textarea[name="message"]').fill(text)

    def place_order(self) -> None:
        self.page.get_by_role("link", name="Place Order").click()


class PaymentPage(BasePage):
    path = "/payment"

    def __init__(self, page: Page):
        super().__init__(page)
        self.order_placed_message = page.locator('[data-qa="order-placed"]')
        self.order_confirmation_text = page.get_by_text(
            "Congratulations! Your order has been confirmed!"
        )

    def pay(self, card: dict) -> None:
        page = self.page
        page.locator('[data-qa="name-on-card"]').fill(card["name_on_card"])
        page.locator('[data-qa="card-number"]').fill(card["card_number"])
        page.locator('[data-qa="cvc"]').fill(card["cvc"])
        page.locator('[data-qa="expiry-month"]').fill(card["expiry_month"])
        page.locator('[data-qa="expiry-year"]').fill(card["expiry_year"])
        page.locator('[data-qa="pay-button"]').click()
