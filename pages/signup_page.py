from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.data_generator import User


class SignupPage(BasePage):
    """Account-information form shown after the first signup step."""

    path = "/signup"

    def __init__(self, page: Page):
        super().__init__(page)
        self.form_heading = page.get_by_text("Enter Account Information")
        self.account_created_message = page.locator('[data-qa="account-created"]')
        self.account_deleted_message = page.locator('[data-qa="account-deleted"]')

    def fill_account_details(self, user: User) -> None:
        page = self.page
        page.get_by_role("radio", name="Mr.").check()
        page.locator('[data-qa="password"]').fill(user["password"])
        page.locator('[data-qa="days"]').select_option(user["birth_date"])
        page.locator('[data-qa="months"]').select_option(user["birth_month"])
        page.locator('[data-qa="years"]').select_option(user["birth_year"])
        page.locator('[data-qa="first_name"]').fill(user["first_name"])
        page.locator('[data-qa="last_name"]').fill(user["last_name"])
        page.locator('[data-qa="company"]').fill(user["company"])
        page.locator('[data-qa="address"]').fill(user["address1"])
        page.locator('[data-qa="address2"]').fill(user["address2"])
        page.locator('[data-qa="country"]').select_option(user["country"])
        page.locator('[data-qa="state"]').fill(user["state"])
        page.locator('[data-qa="city"]').fill(user["city"])
        page.locator('[data-qa="zipcode"]').fill(user["zipcode"])
        page.locator('[data-qa="mobile_number"]').fill(user["mobile_number"])
        page.locator('[data-qa="create-account"]').click()

    def continue_after_signup(self) -> None:
        self.page.locator('[data-qa="continue-button"]').click()
