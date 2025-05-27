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
        self.toggle_dark_btn = QPushButton("🌓 Dark Mode", self)

        self.dark_mode_enabled = False
        self.exit_app = False

        '''
        self.ai_checkbox = QCheckBox("Bật AI", self)
        self.ai_checkbox.stateChanged.connect(self.toggle_ai)
        
        self.ai_enabled = False

        self.ai_model = None
        '''

        self.init_ui()
        self.init_tray_icon()
        self.default_stylesheet = self.styleSheet()

    def init_ui(self):
        self.setWindowTitle("Weather App")

        self.emoji_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.emoji_label.setMinimumHeight(180)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(10, 20, 10, 20)

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.weather_button)
        #vbox.addWidget(self.ai_checkbox)
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.toggle_dark_btn)
        hbox.addStretch()
        vbox.addLayout(hbox)
        vbox.addWidget(self.temp_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.discription_label)
        vbox.addWidget(self.advice_label)

        self.setLayout(vbox)
        self.toggle_dark_btn.clicked.connect(self.toggle_dark_mode)

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

        # CSS
        self.setStyleSheet("""
            QLabel, QPushButton{
                font-family: calibri;
            }
            QLabel#city_label{
                font-size: 40px;
                font-style: italic;
            }
            QLineEdit#city_input{
                font-size: 40px;
            }
            QPushButton#weather_button{
                font-size: 30px;
                font-weight: bold;
            }
            QLabel#temp_label{
                font-size: 75px;
            }
            QLabel#emoji_label{
                font-size: 100px;
                font-family: "Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji", sans-serif;
                padding-top: 30px;
                padding-bottom: 30px;
            }
            QLabel#discription_label{
                font-size: 50px;
            }
            QLabel#advice_label {
                font-size: 25px;
                font-style: italic;
                padding-top: 20px;
            }
        """)
        self.setMinimumSize(800, 700)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_clothing_advice(self, advice):
        self.advice_label.setText(advice)

    def enable_dark_mode(self):
        try:
            with open(r"C:\Users\Dell\PycharmProjects\Weather\dark", "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print("⚠️ Không tìm thấy file dark.css!")

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
            event.accept()  # Cho phép thoát thật
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
'''
    def toggle_ai(self):
        """Kích hoạt/tắt AI khi checkbox thay đổi."""
        self.ai_enabled = self.ai_checkbox.isChecked()

        if self.ai_enabled:
            self.start_ai_model()  # Khởi tạo và chạy mô hình AI khi bật AI
        else:
            self.stop_ai_model()  # Dừng mô hình AI khi tắt AI

    def start_ai_model(self):
        """Khởi tạo và chạy mô hình AI."""
        if self.ai_model is None:
            # Khởi tạo mô hình AI (chỉ khởi tạo khi AI được bật)
            self.ai_model = AI_Model()  # Thay bằng tên lớp mô hình AI của bạn
            self.ai_model.run()  # Chạy mô hình nếu cần thiết
            self.advice_label.setText("AI đã được kích hoạt. Sẵn sàng gợi ý trang phục.")

    def stop_ai_model(self):
        """Dừng mô hình AI."""
        if self.ai_model is not None:
            self.ai_model.stop()  # Dừng mô hình nếu đang chạy
            self.ai_model = None  # Giải phóng bộ nhớ
            self.advice_label.clear()
'''