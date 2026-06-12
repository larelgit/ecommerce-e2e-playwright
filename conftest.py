"""Shared fixtures and browser-level tweaks."""
import re

import pytest

# The target site is ad-supported; ad iframes sometimes cover buttons and
# intercept clicks, so all ad/analytics requests are dropped at network level.
AD_HOSTS = re.compile(
    r"(googlesyndication|doubleclick|adservice|google-analytics|googletagmanager)"
)


@pytest.fixture(autouse=True)
def block_ads(context):
    context.route(AD_HOSTS, lambda route: route.abort())
