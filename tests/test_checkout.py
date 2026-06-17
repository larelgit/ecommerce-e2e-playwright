"""Checkout: the guest gate and the full purchase journey (the suite's showcase)."""
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage, PaymentPage
from pages.flows import register_via_ui
from pages.product_page import ProductPage
from utils.data_generator import User, generate_payment_card


def test_checkout_requires_login(page: Page):
    """Guests can fill a cart, but checkout must ask them to sign in."""
    products = ProductPage(page)
    products.open()
    products.add_to_cart(0)
    products.go_to_cart_from_modal()

    cart = CartPage(page)
    cart.proceed_to_checkout()
    expect(cart.checkout_login_prompt).to_be_visible()


def test_full_purchase_flow(page: Page, new_user: User):
    """Registration -> product -> cart -> checkout -> payment -> confirmation."""
    signup = register_via_ui(page, new_user)

    products = ProductPage(page)
    products.open()
    added_name = products.add_to_cart(0)
    products.go_to_cart_from_modal()

    cart = CartPage(page)
    expect(cart.rows).to_have_count(1)
    cart.proceed_to_checkout()

    # the delivery address must match the data given at registration
    checkout = CheckoutPage(page)
    expect(checkout.address_details_heading).to_be_visible()
    expect(checkout.delivery_address).to_contain_text(new_user["address1"])
    expect(checkout.delivery_address).to_contain_text(new_user["city"])
    expect(checkout.review_order_heading).to_be_visible()
    expect(page.get_by_text(added_name).first).to_be_visible()

    checkout.add_order_comment("Please deliver on a weekday morning.")
    checkout.place_order()

    payment = PaymentPage(page)
    payment.pay(generate_payment_card())
    expect(payment.order_placed_message).to_be_visible()
    expect(payment.order_confirmation_text).to_be_visible()

    # leave no trace behind; this also verifies account deletion while logged in
    payment.delete_account()
    expect(signup.account_deleted_message).to_be_visible()
