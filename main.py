import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, Qt


def main():
    # Set environment variables for faster PyQt5 startup
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

    app = QApplication(sys.argv)

    # Set application properties for better performance (PyQt5 syntax)
    try:
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # Fallback for older PyQt5 versions
        pass

    # Show splash or loading indicator while importing heavy modules
    print("Starting Weather App...")

    # Import UI and controller after QApplication is created
    # This prevents blocking the entire startup process
    from ui import WeatherUI
    from controller import WeatherController

    # Create and show the main window
    view = WeatherUI()
    controller = WeatherController(view)

    # Set a smaller size similar to Windows 11 Task Manager
    view.resize(480, 360)  # Similar to Task Manager compact view

    # Show the window immediately
    view.show()

    # Optional: Show a brief startup message
    def clear_startup_message():
        if hasattr(view, 'temp_label'):
            view.temp_label.setText("")
            view.emoji_label.setText("")

    # Set a startup message that clears after 1 second
    view.temp_label.setText("Weather App Ready!")
    view.temp_label.setStyleSheet("font-size: 40px;")
    view.emoji_label.setText("🌤️")

    # Clear the message after 2 seconds
    QTimer.singleShot(2000, clear_startup_message)

    print("Weather App loaded successfully!")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()