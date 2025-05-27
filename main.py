import sys
from PyQt5.QtWidgets import QApplication
from ui import WeatherUI
from controller import WeatherController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = WeatherUI()
    controller = WeatherController(view)
    view.show()
    sys.exit(app.exec_())
