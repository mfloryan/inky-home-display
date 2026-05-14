# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Check @README.md for project overview and development commands

## Architecture

### Core Components

- **`update_display.py`** - Main entry point that orchestrates data collection and display rendering
- **`display.py`** - Core rendering logic for the e-paper display, handles layout and drawing
- **`display_backend.py`** - Backend abstraction layer for different display outputs (Inky hardware vs PNG)
- **`fonts.py`** - Font management and loading utilities for display rendering

### Data Sources (`src/data/`)

- **`tibber.py`** - Tibber energy API integration for electricity prices and consumption data
- **`weather.py`** - OpenWeather API integration for weather forecasts and conditions
- **`public_transport.py`** - Stockholm public transport (SL API) integration
- **`thermia.py`** - Reads outdoor temperature from Thermia heatpump via Modbus (no caching — always live)
- **`house_sensors.py`** - Fetches indoor room temperatures from local sensor endpoint (no caching — always live)
- **`cache.py`** - File-based caching system to minimise API calls
- **`tokens.py`** - Loads API tokens from local files

### Data Flow

1. Data sources in `src/data/` are called — some cached (Tibber, OpenWeather, SL), some always live (thermia, house sensors)
2. Cached responses are stored as JSON files in `src/cache/` with time-based expiration
3. Data is assembled into a dict and passed to `display.py`
4. `display.py` builds ViewData objects and renders widgets onto the e-ink display using Pillow
5. Output can be either sent to physical Inky display or saved as PNG for development

### API Configuration

API tokens are stored in local files (not in version control):

- `src/tibber-api-token` - Tibber energy API token
- `src/openweather-api-token` - OpenWeather API token

### Caching Strategy

The cache system uses timestamped JSON files in `/out/cache/`:

- Energy prices: `tibber-prices-YYYYMMDD.json` (daily cache)
- Energy stats: `tibber-stats-YYYYMMDD-HH.json` (hourly cache)
- Weather: Similar time-based caching to respect API rate limits

### Display Characteristics

The application targets a 3-color e-ink display (black, yellow, white) with specific UI elements:

- Polish language for weather descriptions and energy statistics
- Energy price graphs with current hour highlighting
- Real-time energy production/consumption data
- Weather forecast with temperature and conditions, including live outdoor temperature from the heatpump (`zewn.`)
- Indoor room temperatures (Salon, Sypialnia, Kuchnia) from local sensors
- Timestamp showing last update

## Widget Architecture

### Design Pattern
Widgets follow a clean separation of concerns: data preparation happens in `generate_content()`, while widgets are pure rendering functions.

### ViewData Classes
Widgets that receive complex data use ViewData dataclasses to define their exact data requirements:

```python
# Data preparation in generate_content()
weather_view_data = WeatherViewData(
    name=data["weather"]["name"],
    sunrise=data["weather"]["sunrise"],
    sunset=data["weather"]["sunset"],
    now_temp=data["weather"]["now"]["temp"],
    forecast=[ForecastItem(...) for forecast in data["weather"]["forecast"]]
)

# Widget only renders the prepared data
WeatherWidget(bounds, font_loader, weather_view_data)
```

### Current Widgets
- **EnergyStatsWidget** - Uses `EnergyData` ViewData (production, consumption, profit, cost)
- **EnergyPriceGraphWidget** - Uses `EnergyPriceData` ViewData (day_prices, current_quarter)
- **EnergyPriceLabelsWidget** - Uses `EnergyPriceData` ViewData (shared with graph)
- **WeatherWidget** - Uses `WeatherViewData` and `ForecastItem` ViewData classes; optionally renders heatpump outdoor temp via `heatpump_outdoor_temp`
- **HouseTempsWidget** - Uses `HouseTempsViewData` with a list of `HouseTempReading` (label + temp)
- **TransportWidget** - Uses `TransportViewData` with a list of `DepartureViewData`
- **HeaderWidget** - Receives `datetime.datetime` directly (no wrapping needed)
- **FooterWidget** - Receives `datetime.datetime` directly (no wrapping needed)

All widgets render at their own (0,0) origin using `TranslatedDraw` for positioning.

## Testing Principles

### Behavior-Driven Testing

- **No "unit tests"** - this term is not helpful. Tests should verify expected behavior, treating implementation as a black box
- Test through the public API exclusively - internals should be invisible to tests
- No 1:1 mapping between test files and implementation files
- Tests that examine internal implementation details are wasteful and should be avoided
- **Coverage targets**: 100% coverage should be expected at all times, but these tests must ALWAYS be based on business behaviour, not implementation details
- Tests must document expected behaviour

### Test Organization

- All test files live in the `tests/` directory, not in `src/`
- Test files are named `test_*.py` based on the behavior or component being tested
- New tests use behavioural naming: `When*` / `And*` classes with `it_*` methods — e.g. `WhenFetchingHouseTemperatures` / `it_returns_none_when_request_fails`
- Older tests use `TestFoo` classes with `test_*` methods — both styles are collected by pytest
- Use Arrange-Act-Assert pattern with clear comments separating sections

### When NOT to Write Tests

- When existing code already handles and validates the behavior (e.g., if display.py checks for None, don't write tests that None is passed correctly)
- When the behavior is already covered by higher-level behavioral tests
- When a simple code change doesn't introduce new behavior (e.g., renaming variables, formatting)
- Don't write tests that duplicate what other tests already verify
- If in doubt whether a test adds value, consider: does this test document a behavior users care about?

### Visual Regression Tests

- Visual regression tests (in `test_visual_regression.py`) only test the happy path with all data sources working correctly
- These tests detect unintended visual changes in the rendered display output
- Do NOT add tests for error scenarios or missing data to visual regression tests
- When display changes intentionally, regenerate baselines with `./test-visual-regression.sh gen` then run `make test` to confirm the new baseline passes

### Running Tests

All tests run in Docker via `make test`. This is always the correct command regardless of test type — do not run tests locally.

### Code Style

- Python 3.13 target
- Ruff linter with 88-character line length
- Double quotes for strings
- Tests use `pytest` with `src/` in Python path
- Avoid writing code comments. All code should be readable and self-documenting though clear structure, meaningful variable and method names

### Git Commits

- Do not follow the usual "tell" commit messages style
- Commit messages should read like a history of the project explaining what has changed as a result of the commit
- "Refactor display to use pluggable backend system" is an example of commit message _we want to avoid_
- "More readable drawing of energy graph" is an example of _good_ commit message
- Each commit message should be clear and concise and can be followed with details. Use emoji in the detailed description.
- Include code changes with tests validating the changes in the same commit.
- Any commit message that uses the word "and" is an indication the commit should be split into two (or more)

### Summary

The key is to write clean, testable, functional code that evolves through small, safe increments. Every change should be driven by a test that describes the desired behavior, and the implementation should be the simplest thing that makes that test pass. When in doubt, favor simplicity and readability over cleverness.