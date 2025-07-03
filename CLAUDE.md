# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Inky Home Display is a Python-based home automation dashboard that renders energy prices, weather forecasts, and public transport information to a Pimoroni Inky wHat e-paper display (400x300 pixels). The application integrates with Tibber (Swedish energy provider), OpenWeather API, and Stockholm public transport (SL) to create a smart home information panel.

## Development Commands

### Linting
```bash
ruff check . --fix
```

### Testing
```bash
pytest
```

### Build (Docker)
```bash
docker build --pull --tag inky-display .
docker run --rm -v $(pwd)/src:/code/src -v $(pwd)/out:/code/img/ -v $(pwd)/out/cache:/code/cache inky-display
```

### Run with Options
```bash
# Force PNG output (skip Inky hardware detection)
docker run --rm -v $(pwd)/src:/code/src -v $(pwd)/out:/code/img/ -v $(pwd)/out/cache:/code/cache inky-display python src/update_display.py --png-only

# Custom output filename
docker run --rm -v $(pwd)/src:/code/src -v $(pwd)/out:/code/img/ -v $(pwd)/out/cache:/code/cache inky-display python src/update_display.py --png-only --output img/my-display.png

# On Raspberry Pi with Inky hardware (default behavior)
python src/update_display.py
```

### Deploy
```bash
rsync -arv --exclude '__pycache__/' src/ jagoda.mm:inky/
```

## Architecture

### Core Components

- **`update_display.py`** - Main entry point that orchestrates data collection and display rendering
- **`display.py`** - Core rendering logic for the e-paper display, handles layout and drawing
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

### Summary

The key is to write clean, testable, functional code that evolves through small, safe increments. Every change should be driven by a test that describes the desired behavior, and the implementation should be the simplest thing that makes that test pass. When in doubt, favor simplicity and readability over cleverness.
