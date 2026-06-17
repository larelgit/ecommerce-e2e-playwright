"""Cross-page user flows that several tests share.

Lives outside the page objects because it spans pages (login -> signup),
and outside conftest because it's a reusable action, not a fixture.
"""
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from utils.data_generator import User


def register_via_ui(page: Page, user: User) -> SignupPage:
    """Full UI signup journey ending logged in. Returns the SignupPage
    so callers can chain logout/delete-account checks."""
    login = LoginPage(page)
    login.open()
    login.start_signup(user["name"], user["email"])

    signup = SignupPage(page)
    expect(signup.form_heading).to_be_visible()
    signup.fill_account_details(user)
    expect(signup.account_created_message).to_be_visible()
    signup.continue_after_signup()
    expect(signup.logged_in_as(user["name"])).to_be_visible()
    return signup
