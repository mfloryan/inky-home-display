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

## NEXT SESSION TODO: Widget Architecture Improvement

### Current Issue
Widgets currently mix data selection/preparation logic with pure rendering. This violates separation of concerns.

### Current Pattern (problematic):
```python
# Widget does both data selection AND rendering
EnergyStatsWidget(bounds, font_loader, full_energy_stats_dict)
# Inside widget: extract production, consumption, profit, cost from dict
```

### Proposed Pattern (better):
```python
# Separate data preparation from rendering
stats_view = EnergyStatsViewData(production=2.5, consumption=1.8, profit=1.25, cost=0.95)
EnergyStatsWidget(bounds, font_loader, stats_view)
# Widget only renders the exact data it needs
```

### Implementation Steps:
1. **Create ViewData classes** - Simple dataclasses with exactly the data each widget needs
2. **Extract data preparation logic** - Move from widgets to dedicated functions/classes
3. **Refactor widgets** - Make them pure rendering functions
4. **Update tests** - Test data preparation separately from rendering
5. **Clean up duplicate data structures** - EnergyGraphData and EnergyPriceData are identical

### Benefits:
- **Pure widgets** - Only rendering, easier to test
- **Reusable data preparation** - ViewData creation can be tested independently
- **Clear separation** - Data logic vs display logic
- **Better naming** - ViewData classes express intent clearly

### Examples to refactor:
- EnergyStatsWidget: needs `production`, `consumption`, `profit`, `cost` numbers only
- EnergyPriceLabelsWidget: needs price array + current hour
- HeaderWidget: needs just datetime
- FooterWidget: needs just datetime

## Testing Principles

### Behavior-Driven Testing

- **No "unit tests"** - this term is not helpful. Tests should verify expected behavior, treating implementation as a black box
- Test through the public API exclusively - internals should be invisible to tests
- No 1:1 mapping between test files and implementation files
- Tests that examine internal implementation details are wasteful and should be avoided
- **Coverage targets**: 100% coverage should be expected at all times, but these tests must ALWAYS be based on business behaviour, not implementation details
- Tests must document expected behaviour

### Code Style

- Python 3.11 target
- Ruff linter with 88-character line length
- Double quotes for strings
- Tests use pytest with `src/` in Python path
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