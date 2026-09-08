"""Catalog contracts, product search, and request validation."""

from uuid import uuid4

import pytest
from playwright.sync_api import APIRequestContext

from utils.api import assert_api_response

pytestmark = [pytest.mark.api, pytest.mark.regression]


@pytest.mark.smoke
def test_products_have_required_fields(api: APIRequestContext) -> None:
    body = assert_api_response(api.get("/api/productsList", max_redirects=0), 200)
    products = body["products"]
    assert isinstance(products, list) and products
    ids = []
    for product in products:
        assert isinstance(product["id"], int) and product["id"] > 0
        ids.append(product["id"])
        for key in ("name", "brand"):
            assert isinstance(product[key], str) and product[key].strip()
        assert product["price"].startswith("Rs. ")
        assert int(product["price"].removeprefix("Rs. ")) > 0
        assert product["category"]["category"]
        assert product["category"]["usertype"]["usertype"]
    assert len(ids) == len(set(ids)), "Product IDs must be unique"


def test_products_reject_post(api: APIRequestContext) -> None:
    assert_api_response(
        api.post("/api/productsList", max_redirects=0),
        405,
        "This request method is not supported.",
    )


def test_brands_have_unique_ids_and_nonempty_names(api: APIRequestContext) -> None:
    body = assert_api_response(api.get("/api/brandsList", max_redirects=0), 200)
    brands = body["brands"]
    assert isinstance(brands, list) and brands
    ids = []
    for brand in brands:
        assert isinstance(brand["id"], int) and brand["id"] > 0
        assert isinstance(brand["brand"], str) and brand["brand"].strip()
        ids.append(brand["id"])
    assert len(ids) == len(set(ids)), "Brand IDs must be unique"


@pytest.mark.smoke
def test_search_returns_a_known_product(api: APIRequestContext) -> None:
    catalog = assert_api_response(api.get("/api/productsList", max_redirects=0), 200)
    known_product = catalog["products"][0]
    result = assert_api_response(
        api.post(
            "/api/searchProduct",
            form={"search_product": known_product["name"]},
            max_redirects=0,
        ),
        200,
    )
    assert isinstance(result["products"], list)
    assert known_product in result["products"]


def test_search_with_no_matches_returns_empty_list(api: APIRequestContext) -> None:
    body = assert_api_response(
        api.post(
            "/api/searchProduct",
            form={"search_product": f"no-such-product-{uuid4().hex}"},
            max_redirects=0,
        ),
        200,
    )
    assert body["products"] == []


def test_search_requires_search_parameter(api: APIRequestContext) -> None:
    assert_api_response(
        api.post("/api/searchProduct", form={}, max_redirects=0),
        400,
        "Bad request, search_product parameter is missing in POST request.",
    )
