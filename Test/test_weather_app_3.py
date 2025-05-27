"""
Record and replay test for multiple city lookups in sequence
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


class TestWeatherApp3(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.ui = WeatherUI()

        # Create directory for recorded responses if it doesn't exist
        os.makedirs('test_recordings', exist_ok=True)

        # Define recording file path
        self.recording_file = 'test_recordings/multiple_city_lookups.json'

        # Mock the API call that would happen when button is clicked
        self.weather_api_patcher = patch('weather_api.get_weather')
        self.mock_weather_api = self.weather_api_patcher.start()

        # Record mode - set to False to replay
        self.record_mode = False

    def tearDown(self):
        self.weather_api_patcher.stop()
        self.ui.close()

    def test_multiple_city_lookups(self):
        """Tests looking up multiple cities in sequence"""
        cities = ["New York", "Tokyo", "Paris"]

        if self.record_mode:
            # In record mode, allow real API call and save the responses
            self.weather_api_patcher.stop()

            recordings = []

            for city in cities:
                # Clear previous input
                self.ui.city_input.clear()

                # Enter new city
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

                # Verify the UI state matches the recording
                self.assertEqual(self.ui.temp_label.text(), recording['temp_label'])
                self.assertEqual(self.ui.emoji_label.text(), recording['emoji_label'])
                self.assertEqual(self.ui.discription_label.text(), recording['description_label'])


if __name__ == '__main__':
    unittest.main()