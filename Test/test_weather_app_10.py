"""
Record and replay test for UI responsiveness during API calls
"""
import sys
import unittest
from unittest.mock import patch, MagicMock
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import json
import os
from ui import WeatherUI


class TestWeatherApp10(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.ui = WeatherUI()

        # Create directory for recorded responses if it doesn't exist
        os.makedirs('test_recordings', exist_ok=True)

        # Define recording file path
        self.recording_file = 'test_recordings/ui_responsiveness.json'

        # Mock the API call that would happen when button is clicked
        self.weather_api_patcher = patch('weather_api.get_weather')
        self.mock_weather_api = self.weather_api_patcher.start()

        # Record mode - set to False to replay
        self.record_mode = False

    def tearDown(self):
            self.weather_api_patcher.stop()
            self.ui.close()

    def test_ui_responsiveness(self):
        """Tests UI responsiveness during API calls"""
        if self.record_mode:
            # In record mode, allow real API call but with a delayed response
            self.weather_api_patcher.stop()

            # Start timing
            start_time = time.time()

            # Simulate user input
            QTest.keyClicks(self.ui.city_input, "Tokyo")

            # Get button state before click
            button_enabled_before = self.ui.weather_button.isEnabled()

            # Click the button
            QTest.mouseClick(self.ui.weather_button, Qt.LeftButton)

            # Get button state immediately after click
            button_enabled_during = self.ui.weather_button.isEnabled()

            # Wait for response
            QTest.qWait(3000)  # Wait longer to ensure API call completes

            # Get button state after response
            button_enabled_after = self.ui.weather_button.isEnabled()

            # End timing
            end_time = time.time()

            # Record the UI state and timing information
            recording = {
                'city': "Tokyo",
                'temp_label': self.ui.temp_label.text(),
                'emoji_label': self.ui.emoji_label.text(),
                'description_label': self.ui.discription_label.text(),
                'button_enabled_before': button_enabled_before,
                'button_enabled_during': button_enabled_during,
                'button_enabled_after': button_enabled_after,
                'response_time': end_time - start_time
            }

            with open(self.recording_file, 'w') as f:
                json.dump(recording, f)

            # Restart the patcher
            self.weather_api_patcher.start()
        else:
            # In replay mode, use recorded response
            with open(self.recording_file, 'r') as f:
                recording = json.load(f)

            # Create a delayed mock response to simulate API delay
            def delayed_response(*args, **kwargs):
                time.sleep(1)  # Simulate API delay
                return {
                    'temp': recording['temp_label'],
                    'emoji': recording['emoji_label'],
                    'description': recording['description_label']
                }

            self.mock_weather_api.side_effect = delayed_response

            # Simulate user input
            QTest.keyClicks(self.ui.city_input, recording['city'])

            # Get button state before click
            button_enabled_before = self.ui.weather_button.isEnabled()
            self.assertEqual(button_enabled_before, recording['button_enabled_before'])

            # Click the button
            QTest.mouseClick(self.ui.weather_button, Qt.LeftButton)

            # Get button state immediately after click
            button_enabled_during = self.ui.weather_button.isEnabled()
            self.assertEqual(button_enabled_during, recording['button_enabled_during'])

            # Wait for response
            QTest.qWait(2000)  # Wait for the delayed response

            # Get button state after response
            button_enabled_after = self.ui.weather_button.isEnabled()
            self.assertEqual(button_enabled_after, recording['button_enabled_after'])

            # Verify the UI state matches the recording
            self.assertEqual(self.ui.temp_label.text(), recording['temp_label'])
            self.assertEqual(self.ui.emoji_label.text(), recording['emoji_label'])
            self.assertEqual(self.ui.discription_label.text(), recording['description_label'])

    if __name__ == '__main__':
        unittest.main()