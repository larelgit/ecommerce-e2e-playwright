"""Test data factories. Every test creates its own user, so tests stay independent."""
import uuid
from typing import TypedDict

from faker import Faker

fake = Faker()


class User(TypedDict):
    """Shape of a generated user. Field names mirror the signup form;
    the account API renames some of them (see conftest.registered_user)."""

    title: str
    name: str
    email: str
    password: str
    birth_date: str
    birth_month: str
    birth_year: str
    first_name: str
    last_name: str
    company: str
    address1: str
    address2: str
    country: str
    state: str
    city: str
    zipcode: str
    mobile_number: str


class PaymentCard(TypedDict):
    name_on_card: str
    card_number: str
    cvc: str
    expiry_month: str
    expiry_year: str


def generate_user() -> User:
    first_name = fake.first_name()
    last_name = fake.last_name()
    return {
        "title": "Mr",
        "name": f"{first_name} {last_name}",
        # uuid suffix guarantees uniqueness even across parallel runs
        "email": f"{first_name}.{last_name}.{uuid.uuid4().hex[:8]}@example.com".lower(),
        "password": fake.password(length=12),
        "birth_date": str(fake.random_int(1, 28)),
        "birth_month": str(fake.random_int(1, 12)),
        "birth_year": str(fake.random_int(1970, 2000)),
        "first_name": first_name,
        "last_name": last_name,
        "company": fake.company(),
        "address1": fake.street_address(),
        "address2": fake.secondary_address(),
        "country": "United States",
        "state": fake.state(),
        "city": fake.city(),
        "zipcode": fake.zipcode(),
        "mobile_number": fake.msisdn(),
    }


def generate_payment_card() -> PaymentCard:
    return {
        "name_on_card": fake.name(),
        "card_number": fake.credit_card_number(),
        "cvc": fake.credit_card_security_code(),
        "expiry_month": "12",
        "expiry_year": "2030",
    }
