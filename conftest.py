"""Shared browser configuration and isolated accounts for UI and API tests."""

import re
from collections.abc import Iterator

import pytest
from playwright.sync_api import APIRequestContext, BrowserContext, Playwright

from utils.api import account_payload, assert_api_response, delete_account
from utils.data_generator import User, generate_user

AD_HOSTS = re.compile(
    r"(googlesyndication|doubleclick|adservice|google-analytics|googletagmanager|fundingchoices)"
)


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    """Keep CLI/environment overrides and the ini fallback on xdist workers."""
    return request.config.getoption("base_url") or request.config.getini("base_url")


@pytest.fixture
def context(context: BrowserContext) -> BrowserContext:
    """Configure only requested browser contexts; API tests stay browser-free."""
    context.route(AD_HOSTS, lambda route: route.abort())
    return context


@pytest.fixture
def api(playwright: Playwright, base_url: str) -> Iterator[APIRequestContext]:
    client = playwright.request.new_context(base_url=base_url)
    try:
        yield client
    finally:
        client.dispose()


@pytest.fixture
def new_user(api: APIRequestContext) -> Iterator[User]:
    """Own cleanup before creation, including failed setup and UI registration."""
    user = generate_user()
    try:
        yield user
    finally:
        delete_account(api, user)


@pytest.fixture
def registered_user(api: APIRequestContext, new_user: User) -> User:
    response = api.post(
        "/api/createAccount", form=account_payload(new_user), max_redirects=0
    )
    assert_api_response(response, 201, "User created!")
    return new_user
