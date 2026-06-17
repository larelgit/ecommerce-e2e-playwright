# Copilot instructions — ecommerce-e2e-playwright

## What this repo is
End-to-end UI test suite for the demo shop **automationexercise.com**.
Python + Playwright (sync API) + pytest, Page Object Model. 12 tests across
auth, search, cart, checkout. ~365 LOC. Runs headless in CI on push and PR
across Chromium/Firefox/WebKit.

## Layout
- `pages/` — Page Object Model. One class per page; `base_page.py` holds shared
  navigation (with 5xx retry) and the `parse_price` helper. `flows.py` holds
  cross-page actions (e.g. `register_via_ui`) that several tests reuse.
- `tests/` — one file per area (`test_auth`, `test_search`, `test_cart`,
  `test_checkout`, `test_smoke`). Tests read as business scenarios; no selectors.
- `utils/data_generator.py` — Faker-backed factories returning `TypedDict`s
  (`User`, `PaymentCard`). Every test gets fresh, unique data.
- `conftest.py` — fixtures: API-backed user setup/teardown, ad blocking via
  network route, and a `base_url` fixture (sourced from `pytest.ini`).
- `.github/workflows/tests.yml` — CI matrix.

## How to build / run
```bash
pip install -r requirements.txt   # versions are pinned, do not loosen
playwright install chromium
pytest                            # full suite, chromium
pytest -n 4                       # parallel (data isolation supports it)
pytest --browser firefox          # other engines
```
Tests hit a live third-party site, so transient failures are expected; CI uses
`--reruns 2`. A green local run is the bar before committing.

## Conventions to follow in reviews and changes
- **No `time.sleep()`.** Use Playwright auto-waiting and web-first `expect`.
- **Selectors, in order of preference:** `data-qa` attributes, then stable CSS
  classes, then `get_by_role`. Avoid matching on display text (breaks under
  i18n) and never use XPath. Note: some buttons are `<a>` with no `href`, so
  they have NO ARIA `link` role — `get_by_role("link", ...)` will not find them;
  use the stable class (e.g. `a.check_out`).
- **Page objects hold selectors and actions; tests hold assertions and flow.**
  Don't put raw locators in test files. Reusable multi-page journeys go in
  `pages/flows.py`, not duplicated across tests.
- **Test data is typed.** Extend the `TypedDict`s in `utils/data_generator.py`
  rather than passing loose dicts. The signup form and account API use different
  field names (`first_name` vs `firstname`) — map explicitly, don't rename keys.
- **Every test owns its data** and must be order-agnostic and xdist-safe (unique
  emails via uuid). Don't introduce shared mutable state between tests.
- **Pin dependencies.** `requirements.txt` uses `==`; bump deliberately, never
  switch to `>=`.
- **Don't hardcode `--browser` in `pytest.ini`** — it must stay overridable from
  the CLI and the CI matrix.

## What to flag in PR review
- Any `time.sleep`, XPath, or text-based selector for a button.
- New locators living in `tests/` instead of `pages/`.
- Loosened dependency pins.
- Tests that depend on execution order or another test's side effects.
- New cross-page flows duplicated instead of added to `pages/flows.py`.

## Trust these instructions
Only search the codebase if something here is incomplete or proves wrong.
