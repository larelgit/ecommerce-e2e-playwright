"""Small contract helpers; tests use Playwright's HTTP client directly."""

from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from utils.data_generator import User


def account_payload(user: User) -> dict[str, str | float | bool]:
    """Send only the documented API fields, mapping the two UI field names."""
    return {
        "name": user["name"],
        "email": user["email"],
        "password": user["password"],
        "title": user["title"],
        "birth_date": user["birth_date"],
        "birth_month": user["birth_month"],
        "birth_year": user["birth_year"],
        "firstname": user["first_name"],
        "lastname": user["last_name"],
        "company": user["company"],
        "address1": user["address1"],
        "address2": user["address2"],
        "country": user["country"],
        "zipcode": user["zipcode"],
        "state": user["state"],
        "city": user["city"],
        "mobile_number": user["mobile_number"],
    }


def response_json(response: APIResponse) -> dict[str, Any]:
    """Check HTTP before decoding: this API carries application codes in JSON."""
    assert response.status == 200, (
        f"{response.url}: HTTP {response.status}; "
        f"Location={response.headers.get('location', '<none>')}. "
        "An unexpected redirect/HTML response can indicate a site access challenge."
    )
    try:
        body = response.json()
    except ValueError:
        raise AssertionError(
            f"{response.url}: expected API JSON, received "
            f"{response.headers.get('content-type', '<unknown>')}; "
            "check target availability/access challenges."
        ) from None
    assert isinstance(body, dict), f"{response.url}: expected a JSON object"
    return body


def assert_api_response(
    response: APIResponse, code: int, message: str | None = None
) -> dict[str, Any]:
    body = response_json(response)
    assert body.get("responseCode") == code, (
        f"{response.url}: expected responseCode={code}, "
        f"got {body.get('responseCode')}; message={body.get('message')}"
    )
    if message is not None:
        assert body.get("message") == message
    return body


def delete_account(api: APIRequestContext, user: User) -> None:
    """Accept an already removed account, but report all other cleanup failures."""
    response = api.delete(
        "/api/deleteAccount",
        form={"email": user["email"], "password": user["password"]},
        max_redirects=0,
    )
    body = response_json(response)
    assert (body.get("responseCode"), body.get("message")) in {
        (200, "Account deleted!"),
        (404, "Account not found!"),
    }, f"Unexpected account cleanup response: {body.get('message')}"
