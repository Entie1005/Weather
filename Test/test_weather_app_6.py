"""
Record and replay test for API timeout handling
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


class TestWeatherApp6(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.ui = WeatherUI()

        # Create directory for recorded responses if it doesn't exist
        os.makedirs('test_recordings', exist_ok=True)

        # Define recording file path
        self.recording_file = 'test_recordings/api_timeout.json'

        # Mock the API call that would happen when button is clicked
        self.weather_api_patcher = patch('weather_api.get_weather')
        self.mock_weather_api = self.weather_api_patcher.start()

        # Record mode - set to False to replay
        self.record_mode = False

    def tearDown(self):
        self.weather_api_patcher.stop()
        self.ui.close()

    def test_api_timeout(self):
        """Tests behavior when API times out"""
        if self.record_mode:
            # In record mode, we need to simulate a timeout
            # This would normally come from the real API

            # For recording purposes, we'll mock a timeout error
            self.mock_weather_api.side_effect = TimeoutError("API connection timed out")

            # Simulate user input
            QTest.keyClicks(self.ui.city_input, "London")
            QTest.mouseClick(self.ui.weather_button, Qt.LeftButton)

            # Wait for response
            QTest.qWait(1000)

            # Record the UI state
            recording = {
                'city': "London",
                'temp_label': self.ui.temp_label.text(),
                'emoji_label': self.ui.emoji_label.text(),
                'description_label': self.ui.discription_label.text()
            }

            with open(self.recording_file, 'w') as f:
                json.dump(recording, f)
        else:
            # In replay mode, use recorded response
            with open(self.recording_file, 'r') as f:
                recording = json.load(f)

            # Mock the weather API to simulate timeout
            self.mock_weather_api.side_effect = TimeoutError("API connection timed out")

            # Simulate user input
            QTest.keyClicks(self.ui.city_input, recording['city'])
            QTest.mouseClick(self.ui.weather_button, Qt.LeftButton)

            # Verify the UI state matches the recording
            self.assertEqual(self.ui.temp_label.text(), recording['temp_label'])
            self.assertEqual(self.ui.emoji_label.text(), recording['emoji_label'])
            self.assertEqual(self.ui.discription_label.text(), recording['description_label'])


if __name__ == '__main__':
    unittest.main()