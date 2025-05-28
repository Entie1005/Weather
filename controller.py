from PyQt5.QtCore import Qt, QThread, pyqtSignal
from model import WeatherModel
import string
import requests
from ai import preload_ai_model, is_ai_ready


class WeatherWorker(QThread):
    """Worker thread for fetching weather data"""
    weather_fetched = pyqtSignal(dict)
    error_occurred = pyqtSignal(str, str)  # error_type, message

    def __init__(self, city_name):
        super().__init__()
        self.city_name = city_name
        self.model = WeatherModel()

    def run(self):
        try:
            data = self.model.get_weather_data(self.city_name)
            result = self.model.analyze_weather(data)
            self.weather_fetched.emit(result)
        except ValueError:
            self.error_occurred.emit("value_error", "Không tìm thấy thành phố hoặc phản hồi không hợp lệ.")
        except requests.exceptions.HTTPError as http_error:
            self.error_occurred.emit("http_error", str(http_error))
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("connection_error", "Lỗi kết nối!\nVui lòng kiểm tra kết nối Internet.")
        except requests.exceptions.Timeout:
            self.error_occurred.emit("timeout_error", "Lỗi thời gian chờ.\nYêu cầu quá thời gian cho phép.")
        except requests.exceptions.TooManyRedirects:
            self.error_occurred.emit("redirect_error", "Quá nhiều chuyển hướng. Kiểm tra URL.")
        except requests.exceptions.RequestException as req_error:
            self.error_occurred.emit("request_error", f"Lỗi yêu cầu:\n{req_error}")


class WeatherController:
    def __init__(self, view):
        self.view = view
        self.worker = None

        # Connect signals
        self.view.weather_button.clicked.connect(self.handle_weather_request)

        # Start preloading AI model in background
        preload_ai_model()

    def handle_weather_request(self):
        city_name = self.view.city_input.text().strip()
        if not city_name:
            self.display_error("Vui lòng nhập tên thành phố.")
            return

        # Disable button and show loading
        self.view.weather_button.setEnabled(False)
        self.view.weather_button.setText("Đang tải...")
        self.view.temp_label.setText("Đang lấy dữ liệu thời tiết...")
        self.view.temp_label.setStyleSheet("font-size: 30px;")
        self.view.emoji_label.setText("⏳")
        self.view.discription_label.setText("")
        self.view.advice_label.setText("")

        # Create and start worker thread
        self.worker = WeatherWorker(city_name)
        self.worker.weather_fetched.connect(self.on_weather_fetched)
        self.worker.error_occurred.connect(self.on_error_occurred)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def on_weather_fetched(self, result):
        """Handle successful weather data fetch"""
        self.update_view(result)

    def on_error_occurred(self, error_type, message):
        """Handle errors from worker thread"""
        if error_type == "http_error":
            # Parse HTTP error from message
            try:
                if "401" in message:
                    self.display_error("API key không hợp lệ.")
                elif "404" in message:
                    self.display_error("Không tìm thấy thành phố!")
                elif "500" in message:
                    self.display_error("Lỗi máy chủ nội bộ.")
                elif "502" in message:
                    self.display_error("Bad Gateway.")
                elif "503" in message:
                    self.display_error("Dịch vụ không khả dụng.")
                elif "504" in message:
                    self.display_error("Gateway Timeout.")
                else:
                    self.display_error(f"Lỗi HTTP: {message}")
            except:
                self.display_error("Lỗi kết nối với máy chủ.")
        else:
            self.display_error(message)

    def on_worker_finished(self):
        """Re-enable UI after worker finishes"""
        self.view.weather_button.setEnabled(True)
        self.view.weather_button.setText("OK")
        self.worker = None

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

        # Show AI status if available
        if is_ai_ready():
            self.view.set_clothing_advice(f"🤖 {advice}")
        else:
            self.view.set_clothing_advice(advice)

    def display_error(self, message):
        self.view.temp_label.setStyleSheet("font-size: 30px;")
        self.view.temp_label.setText(message)
        self.view.emoji_label.setText("❌")
        self.view.discription_label.setText("")
        self.view.advice_label.clear()

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