from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtCore import QTimer

from SplashScreen import SplashScreen
from MainDashboard import MainDashboard 


def main():
    app = QApplication([])
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Show splash screen
    # splash = SplashScreen()
    # splash.show()
    
    # Create main window
    main_window = MainDashboard()
    main_window.show()
    # Timer to close splash and show main window
    # QTimer.singleShot(3000,lambda: show_main_window(splash, main_window))
    app.exec()

# def show_main_window(splash, main_window):
#     splash.close()
#     main_window.show()
    
    
if __name__ == "__main__":
    main()