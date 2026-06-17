# E-commerce E2E Test Suite — Playwright + Python

[![e2e-tests](https://github.com/larelgit/ecommerce-e2e-playwright/actions/workflows/tests.yml/badge.svg)](https://github.com/larelgit/ecommerce-e2e-playwright/actions/workflows/tests.yml)

This repo shows how I set up production-grade UI automation for a web shop: **12 end-to-end
tests** covering registration, login, search, cart and checkout, running headless in CI on
every push — with an HTML report and failure screenshots/traces attached to every run.

**Target application:** [automationexercise.com](https://automationexercise.com) — a full
e-commerce site (catalog, accounts, cart, payments) built as an automation target.

## What's covered

| Suite | Tests | Highlights |
|---|---|---|
| `test_smoke.py` | 1 | App is up, home page renders |
| `test_auth.py` | 4 | Signup, login, **wrong password** and **taken email** negative paths |
| `test_search.py` | 2 | Matching results + **empty-result** negative path |
| `test_cart.py` | 3 | Add to cart, quantity × price totals, remove |
| `test_checkout.py` | 2 | Guest checkout gate + **full purchase flow**: registration → product → cart → checkout → payment → order confirmation |

The showcase test is [`test_full_purchase_flow`](tests/test_checkout.py) — the complete
money path a real client pays to keep green.

## Stack

Playwright (Chromium · Firefox · WebKit) · pytest · Page Object Model · Faker ·
pytest-html · pytest-xdist · GitHub Actions

## Run it locally

```bash
pip install -r requirements.txt
playwright install chromium
pytest --html=report.html --self-contained-html

# parallel (data isolation supports it)
pytest -n 4

# a different engine
pytest --browser firefox
```

## Design decisions

- **Page Object Model** — selectors and page flows live in [pages/](pages/), tests read as
  business scenarios.
- **Every test owns its data** — accounts are generated with Faker and created/removed
  through the site's [REST API](https://automationexercise.com/api_list) in fixtures
  ([conftest.py](conftest.py)), so tests are independent and order-agnostic.
- **Resilient selectors** — `get_by_role` / `data-qa` attributes, no brittle XPath.
  Where the markup fights ARIA (e.g. an `<a class="check_out">` with no `href`, which
  therefore has no `link` role), a stable CSS class beats matching on display text.
- **Typed test data** — user/payment factories return `TypedDict`s ([utils/data_generator.py](utils/data_generator.py)),
  so editors and `pyright` catch a missing or misspelled field before it reaches the form.
- **No `time.sleep()`** — Playwright auto-waiting and web-first `expect` assertions only.
- **Ad traffic is blocked at network level** — the target site serves ad iframes that can
  cover buttons and steal clicks; a route filter in `conftest.py` keeps runs deterministic.
- **Cross-browser in CI** — the GitHub Actions matrix runs the full suite on Chromium,
  Firefox and WebKit on every push ([.github/workflows/tests.yml](.github/workflows/tests.yml)).
- **Failure diagnostics** — screenshots on failure locally; in CI also Playwright traces,
  uploaded with the HTML report as a per-browser workflow artifact.

## Field notes from automating this target

Real-world issues found and handled while building the suite:

- Third-party ad scripts intermittently overlay call-to-action buttons and intercept
  clicks — the kind of flakiness source you have to engineer around in production suites
  (solved here with network-level request blocking rather than retries or sleeps).
- The shared demo site sheds load with `503 "queue full"` pages for minutes at a time.
  Handled on two levels: page navigation retries on 5xx ([pages/base_page.py](pages/base_page.py)),
  and test-level reruns in CI only — locally failures stay loud. Failure screenshots made
  the diagnosis trivial: the "failing test" screenshot was just the 503 page.
- The signup form and the account API use different field names for the same data
  (`first_name` vs `firstname`), which the data factory has to map explicitly.
- **Search relevance finding:** a strict assertion ("every result name contains the query")
  failed honestly and exposed real behaviour — searching for `dress` also returns
  *"Sleeves Top and Short - Blue & Pink"*. The engine matches fields that are not shown
  on the result card (category/description), so users can't tell why an item matched.
  On a client project this goes straight into the bug tracker as a UX/relevance issue;
  this site is a training target without a public tracker, so it's documented here.

## What I'd add next

- Visual regression checks for key pages.
- An API test layer reusing the same data factories.
- Adopt an open-source target (e.g. RealWorld/Conduit) to file real bug reports upstream.
