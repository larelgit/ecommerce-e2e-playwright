# E-commerce UI + API Test Suite — Playwright + Python

[![e2e-tests](https://github.com/larelgit/ecommerce-e2e-playwright/actions/workflows/tests.yml/badge.svg)](https://github.com/larelgit/ecommerce-e2e-playwright/actions/workflows/tests.yml)

Production-style automation for a web shop: **12 UI tests and 15 API tests** covering
accounts, authentication, search, cart and checkout. Five offline infrastructure tests
check URL configuration and browser-free API fixtures. CI runs Ruff, Pyright and smoke
checks on pull requests, with full regression on `main` and a weekday schedule.

**Target application:** [Automation Exercise](https://automationexercise.com), a public
training shop. The live suites create temporary accounts and delete them afterwards.
They depend on the site's availability and its access policy for the runner's network.

## Coverage

| Suite | Tests | Main checks |
|---|---:|---|
| `tests/ui/test_smoke.py` | 1 | Home page title and featured products |
| `tests/ui/test_auth.py` | 4 | Registration, login, wrong password, existing email |
| `tests/ui/test_search.py` | 2 | Matching products and no results |
| `tests/ui/test_cart.py` | 3 | Add, quantity × price totals, remove |
| `tests/ui/test_checkout.py` | 2 | Guest gate and complete purchase journey |
| `tests/api/test_accounts.py` | 9 | Create/read back account, duplicate email, valid/invalid login, missing credentials, unsupported method, delete and reject subsequent login |
| `tests/api/test_products.py` | 6 | Product/brand structure, unique IDs, unsupported method, known-product search, no results, missing query |
| `tests/unit/test_fixtures.py` | 5 | URL precedence in real serial/xdist sessions and API fixture without a browser |

The full purchase test covers registration → product → cart → delivery address →
payment → confirmation → account deletion. Card details are generated test data for
this training target.

## Local setup

Requires Python 3.12+. From the repository root:

```bash
# Creates a local environment and installs project dependencies into it.
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

# Downloads Chromium into the user's Playwright cache.
playwright install chromium
pytest -m smoke --html=reports/smoke.html --self-contained-html
```

`python -m pip install -r requirements.txt` remains a compatibility entry point for
the same installation. Direct dependency pins, including Playwright itself, live in
[pyproject.toml](pyproject.toml), alongside pytest, Ruff and Pyright configuration.
Transitive dependencies are resolved by pip; this is not a complete lockfile.

For all three engines, `playwright install chromium firefox webkit` downloads the
browser binaries. On Ubuntu, `playwright install --with-deps chromium firefox webkit`
**also installs system packages via apt and may require sudo**. Use it when the browser
reports missing shared libraries.

## Select a suite

Run these commands inside the activated virtual environment:

```bash
pytest -m smoke                         # 8 checks: 4 UI + 4 API
pytest -m regression                    # all 27 live UI/API checks
pytest -m api                           # 15 API checks; no browser install needed
pytest -m 'ui and smoke'                 # 4 quick UI checks
pytest -m critical                      # account, cart and full purchase journeys
pytest tests/unit                       # 5 offline infrastructure checks
pytest tests/ui --browser firefox -n 2   # full UI suite in another engine
pytest                                  # all 32 checks, Chromium for UI

ruff check .
ruff format --check .
pyright
```

`smoke` and `critical` are subsets of `regression`. `ui` and `api` select a layer;
`unit` selects offline checks. Unknown markers and configuration keys fail collection.

The same base URL is used for UI and API setup. Precedence is `--base-url`, then
`PYTEST_BASE_URL`, then the default in `pyproject.toml`; this also works with xdist.
Use an override only for a compatible, authorized instance of the target.

## CI

| Trigger | Quality | API | UI |
|---|---|---|---|
| Pull request | Ruff, formatting, Pyright, collection, unit tests | 4 smoke tests | 4 smoke tests, Chromium |
| Push to `main` | Same | All 15 | All 12 per engine: Chromium, Firefox, WebKit |
| Weekdays at 05:23 UTC / manual run | Same | All 15 | All 12 per engine |

The [workflow](.github/workflows/tests.yml) checks API availability before the API
suite and browser access before each UI suite. It runs API tests once, then runs the
browser jobs one at a time with two workers each. Superseded runs are cancelled.
This limits traffic to the shared demo site. Persistent failures remain failures;
there are no blanket reruns or skips that turn an inaccessible target green.

HTML reports, JUnit XML and preflight JSON are uploaded for 14 days. UI failures also
include screenshots and Playwright traces. Artifacts are uploaded even when preflight
fails; an HTML report exists only if pytest actually ran.

## Design decisions

- **Page Object Model:** selectors and actions live in [pages/](pages/); tests express
  scenarios. Shared registration steps live in `pages/flows.py`.
- **Independent data:** fixtures generate unique accounts and register cleanup before
  creation. Cleanup accepts an already deleted account and reports other errors.
- **Browser-free API layer:** [tests/api/](tests/api/) uses Playwright request contexts.
  Ad blocking is attached only when a UI test requests a browser context.
- **API contracts:** tests check transport, application status, messages and relevant
  response data against the [published API scenarios](https://automationexercise.com/api_list).
  This target returns HTTP 200 even for application errors; `responseCode` in JSON
  carries codes such as 400 or 404. Unexpected redirects are exposed at the first hop.
- **Typed data:** `User` and `PaymentCard` describe factory outputs. Account payloads
  explicitly map `first_name`/`last_name` to the API's `firstname`/`lastname`.
- **Readiness and diagnostics:** navigation waits for DOM readiness, checks HTTP errors
  and waits briefly for known access-interstitial titles to disappear. It then reports
  a target-access error if the challenge persists. Controls use Playwright auto-waiting.
- **Dependency checks:** Ruff and Pyright run in CI. Offline fixture checks protect the
  CLI/environment URL precedence and ensure API tests cannot silently start a browser.

## Findings and bug reporting

The [CI failure analysis](docs/ci-troubleshooting.md) links to the actual failing run.
Its Chromium/Firefox jobs received an access challenge (`One moment, please...`),
while account API requests entered HTTP 302 loops. Changing selectors cannot resolve a
persistent site-side access restriction; the runner needs access to the training target.

A [reproduced open-source bug report](docs/bugs/BUG-001-base-url-xdist.md) includes a
minimal offline example of an ini-configured URL becoming `None` on xdist workers.
This is a confirmation of an existing upstream issue, with the workaround covered by
our fixture tests. It is not presented as a newly discovered or newly submitted defect.

**Search field note:** searching for `dress` has returned products whose displayed names
do not contain that term. The public scenarios do not define name-only matching. The
matching fields and expected relevance need owner confirmation, so this remains an
observation rather than a confirmed product defect. The API suite additionally checks
that a search using an actual catalog product name returns that exact product.

## Possible next steps

- Visual regression for key pages.
- A locally hosted open-source shop for deterministic CI independent of the public demo.
- A generated lockfile for transitive dependencies.
