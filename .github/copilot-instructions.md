# Copilot instructions — ecommerce-e2e-playwright

## Project

Production-style Python + synchronous Playwright + pytest suite for the public training
shop automationexercise.com: 12 UI, 15 API and 5 offline infrastructure checks.

## Layout

- `pages/`: selectors/actions; shared journeys in `flows.py`.
- `tests/ui/`: UI scenarios; `tests/api/`: HTTP contracts without a browser.
- `tests/unit/`: offline subprocess checks of real pytest fixture behavior.
- `utils/data_generator.py`: typed Faker factories; `utils/api.py`: payload/contract helpers.
- `conftest.py`: URL precedence, on-demand browser configuration, isolated account fixtures.
- `scripts/check_target.py`: read-only CI preflight and JSON diagnostics.
- `pyproject.toml`: pinned direct dependencies and pytest/Ruff/Pyright configuration.
- `.github/workflows/tests.yml`: PR smoke; main/scheduled/manual regression.
- `docs/`: verified failure analysis and an upstream bug reproduction.

## Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
playwright install chromium
ruff check .
ruff format --check .
pyright
pytest tests/unit
pytest -m api
pytest tests/ui -n 2
```

## Conventions

- Pin direct dependencies in `pyproject.toml`; `requirements.txt` only forwards to it.
- Mark live tests `regression` and exactly one of `ui`/`api`. Add `smoke`/`critical`
  deliberately. Offline tests use `unit` and run in the quality job.
- Keep selectors in page objects and assertions in tests. Prefer `data-qa`, accessible
  roles and stable CSS. An anchor without `href` may not have an ARIA link role.
- No arbitrary sleeps or blanket reruns. Keep access challenges and outages visible.
- Every created user needs fixture-owned cleanup, including when setup fails.
- Keep user/card data typed; map UI/API field names explicitly.
- API calls disable redirect following, check HTTP before parsing JSON, and then check
  the target's application-level `responseCode`. Do not assert HTTP 201 for account creation.
- Preserve CLI > environment > config URL precedence on xdist workers.
- API/unit tests must work without installed browser binaries.
- Keep browser CLI selection overridable. Limit live tests to two workers and serialize
  browser engines in CI to avoid overloading the shared target.
- Verify product requirements before reporting a search-relevance observation as a bug.
- Run relevant local checks and report any target availability limitation honestly.
