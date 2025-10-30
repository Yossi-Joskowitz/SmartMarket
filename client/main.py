from PySide6.QtWidgets import QApplication, QMessageBox
from mainDashboard.dashboard_presenter import create_main_dashboard 
from loginWindow.login_presenter import login_page
from theme_manager import ThemeManager
from thread_manager import run_in_worker

@run_in_worker
def WakeUpServer():
    import requests
    import os
    url = os.getenv("URL", "http://localhost:8000")
    try:
        requests.get(url + "/healthz", timeout=5)
    except Exception:
        pass


def main():
    app = QApplication([])
    ThemeManager.instance().apply(app) 

    success, user_info = login_page()
    if not success:
        QMessageBox.warning(None, "Login Failed", "Login failed or was cancelled")
        return

    # Create main window with user info
    main_window = create_main_dashboard(user_info)
    main_window.show()
    app.exec()


if __name__ == "__main__":
    WakeUpServer()
    main()