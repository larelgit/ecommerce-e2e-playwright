import re

from playwright.sync_api import Locator, Page, expect

from utils.target import TargetUnavailableError


class BasePage:
    """Navigation plus the site-wide header that every page shares."""

    path = "/"

    def __init__(self, page: Page):
        self.page = page

    def open(self) -> None:
        # Waiting for DOM readiness avoids slow third-party load events.
        response = self.page.goto(self.path, wait_until="domcontentloaded")
        if response is None or response.status >= 400:
            status = response.status if response else "no response"
            raise TargetUnavailableError(f"GET {self.path}: HTTP {status}")
        # Access challenges can be HTTP 200. Give a transient interstitial time
        # to finish, then report the environment problem before locating controls.
        try:
            expect(self.page).not_to_have_title(
                re.compile(r"one moment|just a moment|attention required", re.I),
                timeout=15_000,
            )
        except AssertionError as error:
            raise TargetUnavailableError(
                f"GET {self.path}: target access challenge ({self.page.title()!r}). "
                "Check the runner's access to the demo site."
            ) from error

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
