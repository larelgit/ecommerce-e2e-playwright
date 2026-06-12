"""Shared fixtures: browser tweaks and test users managed through the site's REST API."""
import re

import pytest
from playwright.sync_api import Playwright

from utils.data_generator import generate_user

# The target site is ad-supported; ad iframes sometimes cover buttons and
# intercept clicks, so all ad/analytics requests are dropped at network level.
AD_HOSTS = re.compile(
    r"(googlesyndication|doubleclick|adservice|google-analytics|googletagmanager)"
)


@pytest.fixture(autouse=True)
def block_ads(context):
    context.route(AD_HOSTS, lambda route: route.abort())


@pytest.fixture
def api(playwright: Playwright, base_url: str):
    """API client for test-data setup/teardown (https://automationexercise.com/api_list)."""
    client = playwright.request.new_context(base_url=base_url)
    yield client
    client.dispose()


def _delete_account(api, user: dict) -> None:
    # idempotent: a 404 response code for an already-deleted account is fine
    api.delete(
        "/api/deleteAccount",
        form={"email": user["email"], "password": user["password"]},
    )


@pytest.fixture
def new_user(api):
    """Fresh user data for UI-registration tests; the account is removed afterwards."""
    user = generate_user()
    yield user
    _delete_account(api, user)


@pytest.fixture
def registered_user(api):
    """An existing account, created through the API so every test owns its data."""
    user = generate_user()
    payload = {
        **user,
        "firstname": user["first_name"],  # the API uses different field names
        "lastname": user["last_name"],
    }
    response = api.post("/api/createAccount", form=payload)
    body = response.json()
    assert body.get("responseCode") == 201, f"user setup failed: {body}"
    yield user
    _delete_account(api, user)
