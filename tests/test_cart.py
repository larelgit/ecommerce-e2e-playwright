"""Cart behaviour: adding, quantity/total maths, and removal."""
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.product_page import ProductPage


def test_add_product_to_cart(page: Page):
    products = ProductPage(page)
    products.open()
    added_name = products.add_to_cart(0)
    products.go_to_cart_from_modal()

    cart = CartPage(page)
    expect(cart.rows).to_have_count(1)
    assert cart.item_names() == [added_name]
    assert cart.item_quantity(0) == 1


def test_cart_total_reflects_quantity(page: Page):
    products = ProductPage(page)
    products.open()
    products.open_details(0)
    unit_price = products.details_price()
    products.set_quantity(3)
    products.add_to_cart_from_details()
    products.go_to_cart_from_modal()

    cart = CartPage(page)
    expect(cart.rows).to_have_count(1)
    assert cart.item_quantity(0) == 3
    assert cart.item_unit_price(0) == unit_price
    assert cart.item_total(0) == unit_price * 3


def test_remove_product_from_cart(page: Page):
    products = ProductPage(page)
    products.open()
    products.add_to_cart(0)
    products.go_to_cart_from_modal()

    cart = CartPage(page)
    expect(cart.rows).to_have_count(1)
    cart.remove_item(0)
    expect(cart.empty_cart_message).to_be_visible()
