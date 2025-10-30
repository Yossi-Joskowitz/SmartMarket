
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

DARK_QSS = """
QWidget { background-color: #1E1E1E; color: #FFFFFF; }
QFrame { background-color: #2B2B2B; }
QSplitter::handle { background: #444444; }
QFrame#Navbar { background-color: #2B2B2B; border-bottom: 2px solid #444444; }
QFrame#Sidebar { background-color: #1E1E1E; border-right: 2px solid #444444; }
QPushButton { background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #444444; border-radius: 10px; padding: 8px 12px; }
QPushButton:hover { background-color: #4C4C4C; }
QPushButton[variant="round"] { border-radius: 20px; width: 40px; height: 40px; font-size: 16px; }
QPushButton[variant="danger"] { background-color: #7A2E2E; border: 1px solid #8A3A3A; color: #FFFFFF; }
QPushButton[variant="danger"]:hover { background-color: #8A3A3A; }
QPushButton:pressed { padding-top: 9px; padding-bottom: 7px; }
QLineEdit { background-color: #1E1E1E; color: #FFFFFF; border: 1px solid #444444; border-radius: 8px; padding: 8px 12px; }
QLineEdit:focus, QLineEdit:hover { border: 2px solid #007ACC; }
QListWidget { background-color: #141414; color: #FFFFFF; border:1px solid #2F2F2F; border-radius:10px; padding:6px; }
QListWidget::item { padding:10px 12px; margin:4px 4px; border-radius:8px; }
QListWidget::item:hover { background:#212121; }
QListWidget::item:selected { background:#2B2B2B; border:1px solid #3F3F3F; }
QScrollBar:vertical { background: #141414; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #363636; min-height: 24px; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QMenu { background-color: rgba(25,25,25,220); border: 1px solid #3E3E3E; border-radius: 14px; padding: 10px; }
QMenu::separator { height: 1px; background: #3A3A3A; margin: 6px 0; }
QTableWidget {background: #23272E;color: #B0B0B0;border: 1px solid #2B2B2B;border-radius: 10px;gridline-color: #2B2B2B;selection-background-color: #00E0FF33;selection-color: #00E0FF;}
QHeaderView::section {background: #23272E;color: #00E0FF;border: none;font-weight: 600;}
QTextEdit {background-color: #1E1E1E;color: #DDDDDD;border: 1px solid #444444;border-radius: 8px;padding: 10px;font-family: 'Courier New', monospace;font-size: 16px;}
QTabWidget::pane {background: #1E1E1E;border: 1px solid #2B2B2B;border-radius: 8px;}
QTabBar::tab {background: #23272E;color: #B0B0B0;border: 1px solid #2B2B2B;padding: 8px 16px;margin-right: 2px;border-top-left-radius: 8px;border-top-right-radius: 8px;}
QTabBar::tab:selected {background: #00E0FF;color: #1E1E1E;font-weight: 600;}
QTabBar::tab:hover {background: #2B2B2B;}
QProgressBar {border: 1px solid #2B2B2B;background: #23272E;border-radius: 4px;color: #B0B0B0;text-align: center;}
QProgressBar::chunk {background: #00E0FF;border-radius: 3px;}
QComboBox, QLineEdit, QWidget#Category {background: #23272E;color: #B0B0B0;border: 1px solid #2B2B2B;border-radius: 8px;padding: 0 8px;}
QComboBox::drop-down {border: none;width: 24px;}
QComboBox::down-arrow {image: none;}
QLabel {color: #B0B0B0;font-weight: 600;}
QLabel#SectionTitle {font-weight: bold; font-size: 14px; color: #00E0FF;}
QLabel#ExplanationText {font-size: 11px; color: #B0B0B0; margin-bottom: 5px;}
QLabel#HelpText {font-size: 10px; color: #888888; margin-bottom: 15px;}
QLabel#PriceDisplay {font-weight: bold; font-size: 14px; color: #00E0FF;}
QLabel#FormTitle {font-weight: bold; font-size: 16px; margin-bottom: 10px;}
"""

LIGHT_QSS = """
QWidget { background-color: #F5F6F8; color: #1A1A1A; }
QFrame { background-color: #FFFFFF; }
QSplitter::handle { background: #D0D5DD; }
QFrame#Navbar { background-color: #FFFFFF; border-bottom: 2px solid #D0D5DD; }
QFrame#Sidebar { background-color: #FAFAFB; border-right: 2px solid #D0D5DD; }
QPushButton { background-color: #F4F4F5; color: #1A1A1A; border: 1px solid #D0D5DD; border-radius: 10px; padding: 8px 12px; }
QPushButton:hover { background-color: #E9EAEE; }
QPushButton[variant="round"] { border-radius: 20px; width: 40px; height: 40px; font-size: 16px; }
QPushButton[variant="danger"] { background-color: #E35D5D; border: 1px solid #D74E4E; color: #FFFFFF; }
QPushButton[variant="danger"]:hover { background-color: #D74E4E; }
QPushButton:pressed { padding-top: 9px; padding-bottom: 7px; }
QLineEdit { background-color: #FFFFFF; color: #1A1A1A; border: 1px solid #D0D5DD; border-radius: 8px; padding: 8px 12px; }
QLineEdit:focus, QLineEdit:hover { border: 2px solid #0EA5E9; }
QListWidget { background-color: #FFFFFF; color: #1A1A1A; border:1px solid #D0D5DD; border-radius:10px; padding:6px; }
QListWidget::item { padding:10px 12px; margin:4px 4px; border-radius:8px; }
QListWidget::item:hover { background:#F2F4F7; }
QListWidget::item:selected { background:#E9EAEE; border:1px solid #CBD5E1; }
QScrollBar:vertical { background: #F2F4F7; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #CBD5E1; min-height: 24px; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QMenu { background-color: rgba(255,255,255,240); border: 1px solid #D0D5DD; border-radius: 14px; padding: 10px; }
QMenu::separator { height: 1px; background: #D0D5DD; margin: 6px 0; }
QTableWidget { background: #FFFFFF; color: #1A1A1A; border: 1px solid #D0D5DD; border-radius: 10px; gridline-color: #E2E8F0; selection-background-color: #0EA5E933; selection-color: #0EA5E9; }
QHeaderView::section { background: #F1F5F9; color: #0EA5E9; border: none; font-weight: 600; }
QTextEdit { background-color: #FFFFFF; color: #1A1A1A; border: 1px solid #D0D5DD; border-radius: 8px; padding: 10px; font-family: 'Courier New', monospace; font-size: 16px; }
QTabWidget::pane { background: #FFFFFF; border: 1px solid #D0D5DD; border-radius: 8px; }
QTabBar::tab { background: #F1F5F9; color: #1A1A1A; border: 1px solid #D0D5DD; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 8px; border-top-right-radius: 8px; }
QTabBar::tab:selected { background: #0EA5E9; color: #FFFFFF; font-weight: 600; }
QTabBar::tab:hover { background: #E2E8F0; }
QProgressBar { background: #FFFFFF; border: 1px solid #D0D5DD; border-radius: 4px; color: #1A1A1A; text-align: center; }
QProgressBar::chunk { background: #0EA5E9; border-radius: 3px; }
QComboBox, QLineEdit, QWidget#Category { background: #FFFFFF; color: #1A1A1A; border: 1px solid #D0D5DD; border-radius: 8px; padding: 0 8px; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow { image: none; }
QLabel { color: #1A1A1A; font-weight: 600; }
QLabel#SectionTitle {font-weight: bold; font-size: 14px; color: #0EA5E9;}
QLabel#ExplanationText {font-size: 11px; color: #666666; margin-bottom: 5px;}
QLabel#HelpText {font-size: 10px; color: #888888; margin-bottom: 15px;}
QLabel#PriceDisplay {font-weight: bold; font-size: 14px; color: #0EA5E9;}
QLabel#FormTitle {font-weight: bold; font-size: 16px; margin-bottom: 10px;}
"""

class ThemeManager(QObject):
    themeChanged = Signal(str)
    _instance = None

    def __init__(self) -> None:
        super().__init__()
        self.theme = "dark"

    @classmethod
    def instance(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def apply(self, app: QApplication) -> None:
        app.setStyleSheet(DARK_QSS if self.theme == "dark" else LIGHT_QSS)
        self.themeChanged.emit(self.theme)

    def set_theme(self, app: QApplication, theme: str) -> None:
        if theme not in ("dark", "light"):
            return
        self.theme = theme
        self.apply(app)

    def toggle(self, app: QApplication) -> None:
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply(app)
