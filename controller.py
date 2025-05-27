from PyQt5.QtCore import Qt
from model import WeatherModel
import string
import requests

class WeatherController:
    def __init__(self, view):
        self.view = view
        self.model = WeatherModel()

        self.view.weather_button.clicked.connect(self.handle_weather_request)

    def handle_weather_request(self):
        city_name = self.view.city_input.text()
        try:
            data = self.model.get_weather_data(city_name)
            result = self.model.analyze_weather(data)
            self.update_view(result)
        except ValueError:
            self.display_error("Không tìm thấy thành phố hoặc phản hồi không hợp lệ.")
        except requests.exceptions.HTTPError as http_error:
            self.handle_http_error(http_error)
        except requests.exceptions.ConnectionError:
            self.display_error("Lỗi kết nối!\nVui lòng kiểm tra kết nối Internet.")
        except requests.exceptions.Timeout:
            self.display_error("Lỗi thời gian chờ.\nYêu cầu quá thời gian cho phép.")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Quá nhiều chuyển hướng. Kiểm tra URL.")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Lỗi yêu cầu:\n{req_error}")

    def update_view(self, result):
        temp = result["temp_c"]
        weather_id = result["weather_id"]
        description = result["description"]
        advice = result["advice"]

        self.view.temp_label.setStyleSheet("font-size: 75px;")

        # Check if temperature should be displayed in Fahrenheit
        if self.view.is_celsius:
            self.view.temp_label.setText(f"{temp:.0f}°C")
        else:
            fahrenheit_temp = (temp * 9 / 5) + 32
            self.view.temp_label.setText(f"{fahrenheit_temp:.0f}°F")

        self.view.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.view.discription_label.setText(string.capwords(description))
        self.view.set_clothing_advice(advice)

    def display_error(self, message):
        self.view.temp_label.setStyleSheet("font-size: 30px;")
        self.view.temp_label.setText(message)
        self.view.emoji_label.setText("")
        self.view.discription_label.setText("")
        self.view.advice_label.clear()

    def handle_http_error(self, http_error):
        match http_error.response.status_code:
            case 400:
                self.display_error("Yêu cầu không hợp lệ.")
            case 401:
                self.display_error("API key không hợp lệ.")
            case 403:
                self.display_error("Truy cập bị từ chối!")
            case 404:
                self.display_error("Không tìm thấy thành phố!")
            case 500:
                self.display_error("Lỗi máy chủ nội bộ.")
            case 502:
                self.display_error("Bad Gateway.")
            case 503:
                self.display_error("Dịch vụ không khả dụng.")
            case 504:
                self.display_error("Gateway Timeout.")
            case _:
                self.display_error(f"Lỗi HTTP không xác định: {http_error}")

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif 500 <= weather_id <= 504:
            return "🌧️"
        elif weather_id == 511:
            return "🌨️"
        elif 520 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 602:
            return "🌨️"
        elif 611 <= weather_id <= 616:
            return "🌨️"
        elif 620 <= weather_id <= 622:
            return "❄️"
        elif 701 <= weather_id <= 781:
            return "🌫️"
        elif weather_id == 800:
            return "☀️"
        elif weather_id == 801:
            return "🌤️"
        elif weather_id == 802:
            return "⛅"
        elif weather_id == 803:
            return "🌥️"
        elif weather_id == 804:
            return "☁️"
        else:
            return ""
