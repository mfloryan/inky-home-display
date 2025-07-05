#!/bin/bash

# Visual regression testing script for Inky Home Display
# Uses pytest-mpl for image comparison with baseline images

case "${1:-test}" in
    "gen")
        echo "Generating baseline images..."
        docker-compose run --rm inky-display-dev pytest --mpl-generate-path=tests/baseline -m manual tests/test_visual_regression.py -v
        ;;
    "test")
        echo "Running visual regression tests..."
        docker-compose run --rm inky-display-dev pytest --mpl --mpl-results-path=out/test-results -m manual tests/test_visual_regression.py -v
        ;;
    *)
        echo "Usage: ./test-visual-regression.sh [gen|test]"
        echo ""
        echo "Commands:"
        echo "  gen   - Generate baseline images for comparison"
        echo "  test  - Run visual regression tests (default)"
        echo ""
        echo "Results are saved to out/test-results/"
        ;;
esac