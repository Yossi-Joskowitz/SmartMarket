from PySide6.QtWidgets import QApplication, QStyleFactory,QDialog
from PySide6.QtCore import QTimer
# from SplashScreen import SplashScreen
from MainDashboard import MainDashboard 
from view.login_view import LoginView
from model.auth_model import AuthModel, AuthResult
from presenter.login_presenter import LoginPresenter


def main():
    app = QApplication([])
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # view = LoginView()
    # model = AuthModel()
    # presenter = LoginPresenter(view, model)

    # # Ensure shutdown no matter how the dialog closes
    # view.finished.connect(lambda _code: presenter.shutdown())
    # ok = (view.exec() == QDialog.DialogCode.Accepted) and (presenter.result is not None)
    # presenter.shutdown()  # idempotent safeguard

    # if not ok:
    #     return

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