# Gemini CLI Context: Inky Home Display

This project is a Python-based home automation dashboard designed to render real-time information onto a Pimoroni Inky wHat e-paper display (400x300 pixels). It integrates energy prices (Tibber), weather forecasts (OpenWeather), and public transport data (Stockholm SL).

## Project Overview

- **Main Technologies**: Python 3.11+, Pillow (PIL) for rendering, `inky` library for hardware interface, `uv` for dependency management.
- **Key Integrations**:
  - **Tibber**: Electricity prices and consumption stats.
  - **OpenWeather**: Forecasts and current conditions.
  - **Stockholm SL**: Public transport departures.
- **Architecture**:
  - **Orchestration**: `update_display.py` fetches data, caches it, and triggers rendering.
  - **Rendering**: `display.py` manages the layout and delegates rendering to individual widgets.
  - **Widgets**: Pure rendering components in `src/widgets/` that use `ViewData` dataclasses for their inputs.
  - **Backends**: `display_backend.py` abstracts the physical Inky display vs. PNG file output.

## Building and Running

### Prerequisites
- Python 3.11+ and `uv` installed.
- API tokens in `src/tibber-api-token` and `src/openweather-api-token` (not in version control).

### Key Commands
- **Run locally (PNG output)**: `uv run src/update_display.py --png-only` (output to `out/test.png`).
- **Run in Docker**: `docker compose run --rm inky-display` (mimics the Pi Zero environment).
- **Deployment**: `./sync.sh` (syncs code and dependencies to the target Raspberry Pi).
- **Dependency Update**: `uv export --no-dev --no-hashes -o requirements-deploy.txt` for server deployment.

## Development Conventions

### Architecture & Style
- **Widget Pattern**: Data preparation happens in `generate_content()` (in `display.py`), while widgets are pure rendering functions receiving `ViewData` objects.
- **Translated Drawing**: Widgets render relative to `(0,0)` using the `TranslatedDraw` wrapper for automatic positioning within the global display coordinates.
- **Localization**: The display UI uses Polish (`pl_PL.utf8`) for labels and descriptions.
- **Linting**: Ruff is used with an 88-character line length limit. Fix issues with `uv run ruff check . --fix`.

### Testing Strategy
- **Behavior-Driven Testing**: Focus on expected behavior and business logic rather than internal implementation details.
- **Test Organization**: All tests are in `tests/`, organized by behavior.
- **Visual Regression**: Uses `pytest-mpl` to compare rendered images against baselines.
  - Run: `./test-visual-regression.sh`
  - Update baselines: `./test-visual-regression.sh gen`
- **CI Validation**: Run the full suite (lint + tests) in Docker via `./validate.sh` or `make test`.

### Git Commit Style
- **Narrative History**: Commit messages should explain *what* changed and *why*, reading like a project history.
- **Avoid "Refactor..."**: Prefer descriptive messages like "More readable drawing of energy graph".
- **Atomic Commits**: If a commit message needs the word "and", split it into multiple commits.

## Key Files
- `src/update_display.py`: Main entry point and data orchestrator.
- `src/display.py`: Layout definition and widget composition.
- `src/widgets/`: Individual UI components (weather, energy, transport).
- `src/cache.py`: File-based caching for API responses.
- `CLAUDE.md`: Highly detailed development and architectural guidance.
