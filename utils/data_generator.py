"""Test data factories. Every test creates its own user, so tests stay independent."""
import uuid

from faker import Faker

fake = Faker()


def generate_user() -> dict:
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


def generate_payment_card() -> dict:
    return {
        "name_on_card": fake.name(),
        "card_number": fake.credit_card_number(),
        "cvc": fake.credit_card_security_code(),
        "expiry_month": "12",
        "expiry_year": "2030",
    }
