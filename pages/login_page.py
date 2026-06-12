from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    """/login hosts both the login form and the first step of signup."""

    path = "/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.login_heading = page.get_by_text("Login to your account")
        self.signup_heading = page.get_by_text("New User Signup!")
        self.login_error = page.get_by_text("Your email or password is incorrect!")
        self.signup_error = page.get_by_text("Email Address already exist!")

    def login(self, email: str, password: str) -> None:
        self.page.locator('[data-qa="login-email"]').fill(email)
        self.page.locator('[data-qa="login-password"]').fill(password)
        self.page.locator('[data-qa="login-button"]').click()

    def start_signup(self, name: str, email: str) -> None:
        self.page.locator('[data-qa="signup-name"]').fill(name)
        self.page.locator('[data-qa="signup-email"]').fill(email)
        self.page.locator('[data-qa="signup-button"]').click()
