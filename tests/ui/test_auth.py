"""Authentication: signup, login, and the negative paths real clients always ask about."""

import pytest
from playwright.sync_api import Page, expect

from pages.flows import register_via_ui
from pages.login_page import LoginPage
from utils.data_generator import User

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.critical
def test_register_new_user(page: Page, new_user: User) -> None:
    signup = register_via_ui(page, new_user)

    # removing the account through the UI doubles as a check of that flow
    signup.delete_account()
    expect(signup.account_deleted_message).to_be_visible()


@pytest.mark.smoke
@pytest.mark.critical
def test_login_with_valid_credentials(page: Page, registered_user: User) -> None:
    login = LoginPage(page)
    login.open()
    expect(login.login_heading).to_be_visible()
    login.login(registered_user["email"], registered_user["password"])

    expect(login.logged_in_as(registered_user["name"])).to_be_visible()


def test_login_with_wrong_password_shows_error(
    page: Page, registered_user: User
) -> None:
    login = LoginPage(page)
    login.open()
    login.login(registered_user["email"], "wrong-" + registered_user["password"])

    expect(login.login_error).to_be_visible()
    expect(login.logged_in_as(registered_user["name"])).not_to_be_visible()


def test_signup_with_taken_email_shows_error(page: Page, registered_user: User) -> None:
    login = LoginPage(page)
    login.open()
    login.start_signup("Another Person", registered_user["email"])

    expect(login.signup_error).to_be_visible()
