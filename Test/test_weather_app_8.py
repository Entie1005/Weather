"""
Record and replay test for whitespace handling in city names
"""
import sys
import unittest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import json
import os
from ui import WeatherUI


class TestWeatherApp8(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.ui = WeatherUI()

        # Create directory for recorded responses if it doesn't exist
        os.makedirs('test_recordings', exist_ok=True)

        # Define recording file path
        self.recording_file = 'test_recordings/whitespace_handling.json'

        # Mock the API call that would happen when button is clicked
        self.weather_api_patcher = patch('weather_api.get_weather')
        self.mock_weather_api = self.weather_api_patcher.start()

        # Record mode - set to False to replay
        self.record_mode = False

    def tearDown(self):
        self.weather_api_patcher.stop()
        self.ui.close()

    def test_whitespace_handling(self):
        """Tests handling of whitespace in city names"""
        if self.record_mode:
            # In record mode, allow real API call and save the responses
            self.weather_api_patcher.stop()

            # Test cases with different whitespace
            city_variants = ["New York", "  New York  ", "New  York", "\tNew York\n"]
            recordings = []

            for city in city_variants:
                # Clear previous input
                self.ui.city_input.clear()

                # Enter city
                QTest.keyClicks(self.ui.city_input, city)
                QTest.mouseClick(self.ui.weather_button, Qt.LeftButton)

                # Wait for response
                QTest.qWait(1000)

                # Record the UI state
                recording = {
                    'city': city,
                    'temp_label': self.ui.temp_label.text(),
                    'emoji_label': self.ui.emoji_label.text(),
                    'description_label': self.ui.discription_label.text()
                }
                recordings.append(recording)

            with open(self.recording_file, 'w') as f:
                json.dump(recordings, f)

            # Restart the patcher
            self.weather_api_patcher.start()
        else:
            # In replay mode, use recorded responses
            with open(self.recording_file, 'r') as f:
                recordings = json.load(f)

            # All variants should produce the same result
            baseline = recordings[0]

            for idx, recording in enumerate(recordings):
                # Set up mock to return appropriate data
                self.mock_weather_api.return_value = {
                    'temp': recording['temp_label'],
                    'emoji': recording['emoji_label'],
                    'description': recording['description_label']
                }

                # Clear previous input
                self.ui.city_input.clear()

                # Enter city
                QTest.keyClicks(self.ui.city_input, recording['city'])
                QTest.mouseClick(self.ui.weather_button, Qt.LeftButton)

                # Verify results are consistent across different whitespace variants
                self.assertEqual(self.ui.temp_label.text(), baseline['temp_label'])
                self.assertEqual(self.ui.emoji_label.text(), baseline['emoji_label'])
                self.assertEqual(self.ui.discription_label.text(), baseline['description_label'])


if __name__ == '__main__':
    unittest.main()