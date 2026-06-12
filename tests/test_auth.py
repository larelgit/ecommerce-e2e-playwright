"""Authentication: signup, login, and the negative paths real clients always ask about."""
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.signup_page import SignupPage


def test_register_new_user(page: Page, new_user: dict):
    login = LoginPage(page)
    login.open()
    expect(login.signup_heading).to_be_visible()
    login.start_signup(new_user["name"], new_user["email"])

    signup = SignupPage(page)
    expect(signup.form_heading).to_be_visible()
    signup.fill_account_details(new_user)
    expect(signup.account_created_message).to_be_visible()

    signup.continue_after_signup()
    expect(signup.logged_in_as(new_user["name"])).to_be_visible()

    # removing the account through the UI doubles as a check of that flow
    signup.delete_account()
    expect(signup.account_deleted_message).to_be_visible()


def test_login_with_valid_credentials(page: Page, registered_user: dict):
    login = LoginPage(page)
    login.open()
    expect(login.login_heading).to_be_visible()
    login.login(registered_user["email"], registered_user["password"])

    expect(login.logged_in_as(registered_user["name"])).to_be_visible()


def test_login_with_wrong_password_shows_error(page: Page, registered_user: dict):
    login = LoginPage(page)
    login.open()
    login.login(registered_user["email"], "wrong-" + registered_user["password"])

    expect(login.login_error).to_be_visible()
    expect(login.logged_in_as(registered_user["name"])).not_to_be_visible()


def test_signup_with_taken_email_shows_error(page: Page, registered_user: dict):
    login = LoginPage(page)
    login.open()
    login.start_signup("Another Person", registered_user["email"])

    expect(login.signup_error).to_be_visible()
