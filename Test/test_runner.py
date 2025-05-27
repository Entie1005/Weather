"""
Script to run all record and replay tests for the Weather App
"""
import unittest
import os
import sys
import argparse

# Import all test cases
from test_weather_app_1 import TestWeatherApp1
from test_weather_app_2 import TestWeatherApp2
from test_weather_app_3 import TestWeatherApp3
from test_weather_app_4 import TestWeatherApp4
from test_weather_app_5 import TestWeatherApp5
from test_weather_app_6 import TestWeatherApp6
from test_weather_app_7 import TestWeatherApp7
from test_weather_app_8 import TestWeatherApp8
from test_weather_app_9 import TestWeatherApp9
from test_weather_app_10 import TestWeatherApp10


def main():
    parser = argparse.ArgumentParser(description='Run record and replay tests for Weather App')
    parser.add_argument('--record', action='store_true', help='Run tests in record mode')
    parser.add_argument('--test', type=str, help='Run specific test (e.g., "1" for test_weather_app_1)')
    args = parser.parse_args()

    # Create test recordings directory if it doesn't exist
    os.makedirs('test_recordings', exist_ok=True)

    # Create test suite
    suite = unittest.TestSuite()

    # Map of test numbers to test classes
    test_map = {
        '1': TestWeatherApp1,
        '2': TestWeatherApp2,
        '3': TestWeatherApp3,
        '4': TestWeatherApp4,
        '5': TestWeatherApp5,
        '6': TestWeatherApp6,
        '7': TestWeatherApp7,
        '8': TestWeatherApp8,
        '9': TestWeatherApp9,
        '10': TestWeatherApp10
    }

    # Set record mode for all tests based on command line argument
    for test_num, test_class in test_map.items():
        for attr in dir(test_class):
            if attr.startswith('__'):
                continue
            try:
                value = getattr(test_class, attr)
                if isinstance(value, type) and issubclass(value, unittest.TestCase):
                    value.record_mode = args.record
            except (TypeError, AttributeError):
                pass

    # Add tests to suite
    if args.test:
        if args.test in test_map:
            suite.addTest(unittest.makeSuite(test_map[args.test]))
        else:
            print(f"Error: Test '{args.test}' not found")
            return
    else:
        # Add all tests
        for test_class in test_map.values():
            suite.addTest(unittest.makeSuite(test_class))

    # Run the tests
    mode = "RECORD" if args.record else "REPLAY"
    print(f"Running tests in {mode} mode")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\nTest Summary:")
    print(f"Run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")

    # Return non-zero exit code if any tests failed
    if result.errors or result.failures:
        sys.exit(1)


if __name__ == '__main__':
    main()

'''
### Commands

To record test data (makes real API calls):
```
python test_runner.py --record
```

To replay tests using recorded data (no real API calls):
```
python test_runner.py
```

To run a specific test:
```
python test_runner.py --test 1
```

## Test Cases

1. **Basic City Lookup**: Tests the core functionality of looking up weather by city name
2. **City Not Found**: Tests error handling when a non-existent city is entered
3. **Multiple City Lookups**: Tests looking up multiple cities in sequence
4. **Empty City Input**: Tests behavior when empty input is submitted
5. **Special Characters**: Tests handling of special characters in city names
6. **API Timeout**: Tests behavior when the weather API times out
7. **Case Insensitivity**: Tests that city names are case insensitive
8. **Whitespace Handling**: Tests proper handling of whitespace in city names
9. **Network Error**: Tests behavior when network errors occur during API calls
10. **UI Responsiveness**: Tests UI responsiveness during API calls
'''