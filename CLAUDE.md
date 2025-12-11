# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Check @README.md for project overview and development commands

## Architecture

### Core Components

- **`update_display.py`** - Main entry point that orchestrates data collection and display rendering
- **`display.py`** - Core rendering logic for the e-paper display, handles layout and drawing
- **`display_backend.py`** - Backend abstraction layer for different display outputs (Inky hardware vs PNG)
- **`fonts.py`** - Font management and loading utilities for display rendering
- **`tibber.py`** - Tibber energy API integration for electricity prices and consumption data
- **`weather.py`** - OpenWeather API integration for weather forecasts and conditions
- **`cache.py`** - File-based caching system to minimize API calls and improve performance
- **`public_transport.py`** - Stockholm public transport (SL API) integration (incomplete)

### Data Flow

1. APIs are called to fetch fresh data (Tibber, OpenWeather, SL)
2. Responses are cached locally as JSON files with time-based expiration
3. Data is processed and formatted for display
4. `display.py` renders the information onto the e-ink display using Pillow
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
- Weather forecast with temperature and conditions
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
- **WeatherWidget** - Uses `WeatherViewData` and `ForecastItem` ViewData classes
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
- Test classes use descriptive names like `TestCacheFunction` or `TestTransportWidget`
- Test method names describe expected behavior: `test_should_return_cached_data_when_cache_file_exists`
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
- When display changes intentionally, regenerate baselines with `./test-visual-regression.sh gen`

### Code Style

- Python 3.11 target
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