from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QSizePolicy, QHBoxLayout, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction


class WeatherUI(QWidget):
    def __init__(self):
        super().__init__()

        self.city_label = QLabel("Nhập tên thành phố: ", self)
        self.city_input = QLineEdit(self)
        self.weather_button = QPushButton("OK", self)
        self.temp_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.discription_label = QLabel(self)
        self.advice_label = QLabel(self)
        self.toggle_dark_btn = QPushButton("🌓", self)
        self.temp_switch_btn = QPushButton("°C", self)
        self.is_celsius = True

        self.dark_mode_enabled = False
        self.exit_app = False

        self.init_ui()
        self.init_tray_icon()
        self.default_stylesheet = self.styleSheet()

    def init_ui(self):
        self.setWindowTitle("Weather App")

        # Enable window resizing by mouse dragging
        self.setWindowFlags(Qt.Window)

        self.emoji_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.emoji_label.setMinimumHeight(30)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(8, 8, 8, 8)
        vbox.setSpacing(3)

        # Top row with city input and dark mode button
        top_row = QHBoxLayout()
        top_row.addWidget(self.city_label)
        top_row.addStretch()
        top_row.addWidget(self.toggle_dark_btn)
        vbox.addLayout(top_row)

        vbox.addWidget(self.city_input)
        vbox.addWidget(self.weather_button)

        vbox.addWidget(self.temp_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.discription_label)
        vbox.addWidget(self.advice_label)

        temp_switch_layout = QHBoxLayout()
        temp_switch_layout.addStretch()
        temp_switch_layout.addWidget(self.temp_switch_btn)
        vbox.addLayout(temp_switch_layout)

        self.setLayout(vbox)
        self.toggle_dark_btn.clicked.connect(self.toggle_dark_mode)
        self.temp_switch_btn.clicked.connect(self.toggle_temperature_unit)

        # Align
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temp_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.discription_label.setAlignment(Qt.AlignCenter)
        self.advice_label.setAlignment(Qt.AlignCenter)

        # Object Names
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.weather_button.setObjectName("weather_button")
        self.temp_label.setObjectName("temp_label")
        self.emoji_label.setObjectName("emoji_label")
        self.discription_label.setObjectName("discription_label")
        self.advice_label.setWordWrap(True)
        self.advice_label.setObjectName("advice_label")
        self.toggle_dark_btn.setObjectName("toggle_dark_btn")
        self.temp_switch_btn.setObjectName("temp_switch_btn")

        # Widget-sized styling
        self.setStyleSheet("""
            QLabel, QPushButton{
                font-family: calibri;
            }
            QLabel#city_label{
                font-size: 12px;
                font-style: italic;
                font-weight: 500;
            }
            QLineEdit#city_input{
                font-size: 12px;
                padding: 3px;
                border-radius: 3px;
                border: 1px solid #ccc;
                max-height: 20px;
            }
            QPushButton#weather_button{
                font-size: 10px;
                font-weight: bold;
                padding: 3px;
                border-radius: 4px;
                background-color: #007ACC;
                color: white;
                border: none;
                max-height: 20px;
            }
            QPushButton#weather_button:hover{
                background-color: #005A9E;
            }
            QPushButton#weather_button:pressed{
                background-color: #004080;
            }
            QPushButton#weather_button:disabled{
                background-color: #CCE4F0;
                color: #888;
            }
            QPushButton#toggle_dark_btn{
                font-size: 8px;
                font-weight: bold;
                padding: 2px 4px;
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4A4A4A, stop:1 #2E2E2E);
                color: white;
                border: 1px solid #666;
                max-height: 14px;
                max-width: 40px;
            }
            QPushButton#toggle_dark_btn:hover{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #5A5A5A, stop:1 #3E3E3E);
                border: 1px solid #777;
            }
            QPushButton#toggle_dark_btn:pressed{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2E2E2E, stop:1 #1A1A1A);
            }
            QLabel#temp_label{
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#emoji_label{
                font-size: 56px;
                font-family: "Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji", sans-serif;
                padding-top: 3px;
                padding-bottom: 3px;
            }
            QLabel#discription_label{
                font-size: 13px;
                font-weight: 500;
            }
            QLabel#advice_label {
                font-size: 9px;
                font-style: italic;
                padding-top: 3px;
                color: #555;
            }
            QPushButton#temp_switch_btn{
                font-size: 8px;
                font-weight: bold;
                min-width: 28px;
                max-width: 28px;
                min-height: 16px;
                max-height: 16px;
                border-radius: 8px;
                background-color: #007ACC;
                color: white;
                border: none;
            }
            QPushButton#temp_switch_btn:hover{
                background-color: #005A9E;
            }
            QPushButton#temp_switch_btn:pressed{
                background-color: #004080;
            }
        """)

        # Set minimum size but allow resizing
        self.setMinimumSize(220, 180)
        self.resize(250, 200)  # Default widget size

        # Enable resizing
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def set_clothing_advice(self, advice):
        self.advice_label.setText(advice)

    def enable_dark_mode(self):
        # Dark mode with same layout and sizing as light mode
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QLabel, QPushButton{
                font-family: calibri;
                color: white;
            }
            QLabel#city_label{
                font-size: 12px;
                font-style: italic;
                font-weight: 500;
                color: white;
            }
            QLineEdit#city_input{
                font-size: 12px;
                padding: 3px;
                border-radius: 3px;
                background-color: #2c2c2c;
                color: white;
                border: 1px solid #555;
                max-height: 20px;
            }
            QPushButton#weather_button{
                font-size: 10px;
                font-weight: bold;
                padding: 3px;
                border-radius: 4px;
                background-color: #3a3a3a;
                color: white;
                border: none;
                max-height: 20px;
            }
            QPushButton#weather_button:hover{
                background-color: #4a4a4a;
            }
            QPushButton#weather_button:pressed{
                background-color: #2a2a2a;
            }
            QPushButton#weather_button:disabled{
                background-color: #555;
                color: #888;
            }
            QPushButton#toggle_dark_btn{
                font-size: 8px;
                font-weight: bold;
                padding: 2px 4px;
                border-radius: 6px;
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                max-height: 14px;
                max-width: 40px;
            }
            QPushButton#toggle_dark_btn:hover{
                background-color: #4a4a4a;
                border: 1px solid #666;
            }
            QPushButton#toggle_dark_btn:pressed{
                background-color: #2a2a2a;
            }
            QLabel#temp_label{
                font-size: 16px;
                font-weight: bold;
                color: white;
            }
            QLabel#emoji_label{
                font-size: 56px;
                font-family: "Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji", sans-serif;
                padding-top: 3px;
                padding-bottom: 3px;
            }
            QLabel#discription_label{
                font-size: 13px;
                font-weight: 500;
                color: white;
            }
            QLabel#advice_label {
                font-size: 9px;
                font-style: italic;
                padding-top: 3px;
                color: #ccc;
            }
            QPushButton#temp_switch_btn{
                font-size: 8px;
                font-weight: bold;
                min-width: 28px;
                max-width: 28px;
                min-height: 16px;
                max-height: 16px;
                border-radius: 8px;
                background-color: #3a3a3a;
                color: white;
                border: none;
            }
            QPushButton#temp_switch_btn:hover{
                background-color: #4a4a4a;
            }
            QPushButton#temp_switch_btn:pressed{
                background-color: #2a2a2a;
            }
        """)

    def toggle_dark_mode(self):
        if self.dark_mode_enabled:
            self.setStyleSheet(self.default_stylesheet)
            self.dark_mode_enabled = False
        else:
            self.enable_dark_mode()
            self.dark_mode_enabled = True

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("weather_icon.png"))

        tray_menu = QMenu()

        restore_action = QAction("Mở lại", self)
        restore_action.triggered.connect(self.show_normal_from_tray)
        tray_menu.addAction(restore_action)

        exit_action = QAction("Thoát", self)
        exit_action.triggered.connect(self.exit_app_completely)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def show_normal_from_tray(self):
        self.showNormal()
        self.activateWindow()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def closeEvent(self, event):
        if self.exit_app:
            event.accept()
        else:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Weather App",
                "Ứng dụng đang chạy nền. Nhấp đúp biểu tượng để mở lại.",
                QSystemTrayIcon.Information,
                2000
            )

    def exit_app_completely(self):
        self.exit_app = True
        self.close()

    def toggle_temperature_unit(self):
        """Toggle between Celsius and Fahrenheit"""
        self.is_celsius = not self.is_celsius
        if self.is_celsius:
            self.temp_switch_btn.setText("°C")
        else:
            self.temp_switch_btn.setText("°F")

        # If there's current temperature data, update the display
        current_temp_text = self.temp_label.text()
        if "°" in current_temp_text and current_temp_text != "":
            # Extract temperature value and convert
            try:
                temp_value = float(current_temp_text.replace("°C", "").replace("°F", "").strip())
                if self.is_celsius:
                    # Convert from Fahrenheit to Celsius
                    celsius_temp = (temp_value - 32) * 5 / 9
                    self.temp_label.setText(f"{celsius_temp:.0f}°C")
                else:
                    # Convert from Celsius to Fahrenheit
                    fahrenheit_temp = (temp_value * 9 / 5) + 32
                    self.temp_label.setText(f"{fahrenheit_temp:.0f}°F")
            except ValueError:
                pass  # If conversion fails, do nothing