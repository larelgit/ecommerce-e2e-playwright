"""Account creation, authentication, deletion, and negative validation."""

import pytest
from playwright.sync_api import APIRequestContext

from utils.api import account_payload, assert_api_response
from utils.data_generator import User, generate_user

pytestmark = [pytest.mark.api, pytest.mark.regression]


@pytest.mark.smoke
@pytest.mark.critical
def test_create_account_persists_details(
    api: APIRequestContext, new_user: User
) -> None:
    assert_api_response(
        api.post("/api/createAccount", form=account_payload(new_user), max_redirects=0),
        201,
        "User created!",
    )
    body = assert_api_response(
        api.get(
            "/api/getUserDetailByEmail",
            params={"email": new_user["email"]},
            max_redirects=0,
        ),
        200,
    )
    saved = body["user"]
    assert saved["id"] > 0
    for key in ("name", "email", "first_name", "last_name", "address1", "city"):
        assert saved[key] == new_user[key]


def test_create_account_rejects_duplicate_email(
    api: APIRequestContext, registered_user: User
) -> None:
    assert_api_response(
        api.post(
            "/api/createAccount",
            form=account_payload(registered_user),
            max_redirects=0,
        ),
        400,
        "Email already exists!",
    )


@pytest.mark.smoke
@pytest.mark.critical
def test_login_with_valid_credentials(
    api: APIRequestContext, registered_user: User
) -> None:
    assert_api_response(
        api.post(
            "/api/verifyLogin",
            form={
                "email": registered_user["email"],
                "password": registered_user["password"],
            },
            max_redirects=0,
        ),
        200,
        "User exists!",
    )


def test_login_rejects_wrong_password(
    api: APIRequestContext, registered_user: User
) -> None:
    assert_api_response(
        api.post(
            "/api/verifyLogin",
            form={
                "email": registered_user["email"],
                "password": "wrong-" + registered_user["password"],
            },
            max_redirects=0,
        ),
        404,
        "User not found!",
    )


def test_login_rejects_unknown_account(api: APIRequestContext) -> None:
    unknown_user = generate_user()
    assert_api_response(
        api.post(
            "/api/verifyLogin",
            form={"email": unknown_user["email"], "password": unknown_user["password"]},
            max_redirects=0,
        ),
        404,
        "User not found!",
    )


@pytest.mark.parametrize("missing_field", ["email", "password"])
def test_login_requires_both_credentials(
    api: APIRequestContext, missing_field: str
) -> None:
    user = generate_user()
    form: dict[str, str | float | bool] = {
        "email": user["email"],
        "password": user["password"],
    }
    del form[missing_field]
    assert_api_response(
        api.post("/api/verifyLogin", form=form, max_redirects=0),
        400,
        "Bad request, email or password parameter is missing in POST request.",
    )


def test_login_rejects_delete_method(api: APIRequestContext) -> None:
    assert_api_response(
        api.delete("/api/verifyLogin", max_redirects=0),
        405,
        "This request method is not supported.",
    )


@pytest.mark.critical
def test_deleted_account_can_no_longer_login(
    api: APIRequestContext, registered_user: User
) -> None:
    credentials: dict[str, str | float | bool] = {
        "email": registered_user["email"],
        "password": registered_user["password"],
    }
    assert_api_response(
        api.delete("/api/deleteAccount", form=credentials, max_redirects=0),
        200,
        "Account deleted!",
    )
    assert_api_response(
        api.post("/api/verifyLogin", form=credentials, max_redirects=0),
        404,
        "User not found!",
    )
