from playwright.sync_api import Locator, Page


class BasePage:
    """Navigation plus the site-wide header that every page shares."""

    path = "/"

    def __init__(self, page: Page):
        self.page = page

    def open(self) -> None:
        # base_url is configured in pytest.ini, so paths stay relative
        self.page.goto(self.path)

    @staticmethod
    def parse_price(text: str) -> int:
        """'Rs. 500' -> 500 (the shop lists whole-rupee prices only)."""
        return int(text.replace("Rs.", "").strip())

    # --- header, present on every page ---

    def go_to_login_page(self) -> None:
        self.page.get_by_role("link", name="Signup / Login").click()

    def go_to_products_page(self) -> None:
        self.page.get_by_role("link", name="Products").click()

    def go_to_cart(self) -> None:
        self.page.get_by_role("link", name="Cart", exact=True).click()

    def logged_in_as(self, name: str) -> Locator:
        return self.page.get_by_text(f"Logged in as {name}")

    def logout(self) -> None:
        self.page.get_by_role("link", name="Logout").click()

    def delete_account(self) -> None:
        self.page.get_by_role("link", name="Delete Account").click()
