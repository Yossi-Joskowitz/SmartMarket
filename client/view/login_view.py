"""
LoginView (PySide6 QDialog) – Stylish version (no functionality changes)
- Bigger dialog, dark gradient background
- Centered "card" with soft shadow
- Clearer inputs, modern tabs, pretty buttons
"""
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor


class LoginView(QDialog):
    # Signals for Presenter (unchanged)
    request_login = Signal(str, str)
    request_signup = Signal(str, str)
    request_send_verification = Signal()
    request_forgot_password = Signal(str)
    request_google_login = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setModal(True)
        self.setMinimumSize(560, 540)  # bigger, nicer canvas

        # ---------- Global style (dark, clean) ----------
        self.setStyleSheet("""
            /* Dialog background */
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #0f172a, stop:1 #111827);
            }

            /* Card container */
            #Card {
                background: #0b1220;
                border: 1px solid #1f2937;
                border-radius: 18px;
            }

            /* Headings */
            #Title {
                color: #e5e7eb;
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 0.3px;
            }
            #Subtitle {
                color: #94a3b8;
                font-size: 13px;
                margin-top: 4px;
            }

            /* Tabs */
            QTabWidget::pane {
                border: 1px solid #1f2937;
                border-radius: 12px;
                background: #0b1220;
                margin-top: 8px;
            }
            QTabBar::tab {
                background: #0b1220;
                color: #cbd5e1;
                border: 1px solid #1f2937;
                padding: 8px 14px;
                margin-right: 6px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #111827;
                color: #e5e7eb;
                border-bottom: 1px solid #111827;
            }
            QTabBar::tab:hover {
                background: #0f172a;
            }

            /* Inputs */
            QLineEdit {
                background: #0b1220;
                color: #e5e7eb;
                border: 1px solid #1f2937;
                border-radius: 10px;
                padding: 10px 12px;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #2563eb;
                background: #0b1426;
            }

            /* Primary button */
            #PrimaryButton {
                background: #22c55e;
                color: #07131a;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
            }
            #PrimaryButton:hover { background: #26d065; }
            #PrimaryButton:pressed { background: #1fb457; }
            #PrimaryButton:disabled { background: #1c4532; color: #9ca3af; }

            /* Secondary button */
            #SecondaryButton {
                background: #111827;
                color: #e5e7eb;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
            }
            #SecondaryButton:hover { background: #0f172a; }
            #SecondaryButton:pressed { background: #0b1220; }
            #SecondaryButton:disabled { color: #94a3b8; border-color: #1f2937; }

            /* Ghost (text) button */
            #GhostButton {
                background: transparent;
                color: #93c5fd;
                border: none;
                padding: 10px 12px;
                font-weight: 600;
            }
            #GhostButton:hover { color: #bfdbfe; text-decoration: underline; }
            #GhostButton:disabled { color: #64748b; }

            /* Google button */
            #GoogleButton {
                background: #1f2937;
                color: #e5e7eb;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
            }
            #GoogleButton:hover { background: #243041; }
            #GoogleButton:pressed { background: #1b2533; }

            /* Labels inside forms */
            QLabel {
                color: #cbd5e1;
                font-size: 12px;
            }
        """)

        # ---------- Card container with shadow ----------
        card = QWidget(objectName="Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(14)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 16)
        shadow.setColor(QColor(0, 0, 0, 140))
        card.setGraphicsEffect(shadow)

        # ---------- Header ----------
        title = QLabel("Welcome to Smart Market", objectName="Title")
        subtitle = QLabel("Sign in to continue", objectName="Subtitle")

        # ---------- Tabs ----------
        self.tabs = QTabWidget()
        self.login_tab = QWidget()
        self.signup_tab = QWidget()
        self.tabs.addTab(self.login_tab, "Sign In")
        self.tabs.addTab(self.signup_tab, "Sign Up")

        # --- Sign In tab ---
        self.login_email = QLineEdit(); self.login_email.setPlaceholderText("Email")
        self.login_pass = QLineEdit(); self.login_pass.setPlaceholderText("Password"); self.login_pass.setEchoMode(QLineEdit.Password)

        form_login = QFormLayout()
        form_login.setSpacing(10)
        form_login.addRow("Email:", self.login_email)
        form_login.addRow("Password:", self.login_pass)

        self.btn_login = QPushButton("Sign In"); self.btn_login.setObjectName("PrimaryButton")
        self.btn_forgot = QPushButton("Forgot password"); self.btn_forgot.setObjectName("GhostButton")
        self.btn_google = QPushButton("Sign in with Google"); self.btn_google.setObjectName("GoogleButton")

        row_login = QHBoxLayout()
        row_login.setSpacing(10)
        row_login.addWidget(self.btn_login)
        row_login.addStretch()
        row_login.addWidget(self.btn_forgot)

        v_login = QVBoxLayout(self.login_tab)
        v_login.setSpacing(12)
        v_login.addLayout(form_login)
        v_login.addLayout(row_login)
        v_login.addWidget(self.btn_google)

        # --- Sign Up tab ---
        self.signup_email = QLineEdit(); self.signup_email.setPlaceholderText("Email")
        self.signup_pass = QLineEdit(); self.signup_pass.setPlaceholderText("Password"); self.signup_pass.setEchoMode(QLineEdit.Password)

        form_signup = QFormLayout()
        form_signup.setSpacing(10)
        form_signup.addRow("Email:", self.signup_email)
        form_signup.addRow("Password:", self.signup_pass)

        self.btn_signup = QPushButton("Create account"); self.btn_signup.setObjectName("PrimaryButton")
        self.btn_send_verif = QPushButton("Send email verification"); self.btn_send_verif.setObjectName("SecondaryButton")

        v_signup = QVBoxLayout(self.signup_tab)
        v_signup.setSpacing(12)
        v_signup.addLayout(form_signup)
        v_signup.addWidget(self.btn_signup)
        v_signup.addWidget(self.btn_send_verif)

        # --- Status label (kept; styles toggled per show_info/show_error) ---
        self.status = QLabel("")
        self.status.setWordWrap(True)
        self.status.setStyleSheet("color:#94a3b8; font-size: 12px; margin-top: 6px;")

        # ---------- Assemble card ----------
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.tabs)
        card_layout.addWidget(self.status)

        # ---------- Root layout: center the card ----------
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30)
        root.addStretch(1)
        root.addWidget(card, 0, Qt.AlignHCenter)
        root.addStretch(1)

        # ---------- Wire signals (unchanged) ----------
        self.btn_login.clicked.connect(self._emit_login)
        self.btn_signup.clicked.connect(self._emit_signup)
        self.btn_send_verif.clicked.connect(lambda: self.request_send_verification.emit())
        self.btn_forgot.clicked.connect(self._emit_forgot)
        self.btn_google.clicked.connect(lambda: self.request_google_login.emit())

        # store signup token/email to allow re-send verification (unchanged)
        self._last_signup_id_token: Optional[str] = None
        self._last_signup_email: Optional[str] = None

    # --- Helpers (unchanged logic) ---
    def _emit_login(self):
        self.request_login.emit(self.login_email.text().strip(), self.login_pass.text())

    def _emit_signup(self):
        self.request_signup.emit(self.signup_email.text().strip(), self.signup_pass.text())

    def _emit_forgot(self):
        email = self.login_email.text().strip() or self.signup_email.text().strip()
        self.request_forgot_password.emit(email)

    def set_busy(self, busy: bool, msg: str = ""):
        self.btn_login.setEnabled(not busy)
        self.btn_signup.setEnabled(not busy)
        self.btn_send_verif.setEnabled(not busy)
        self.btn_forgot.setEnabled(not busy)
        self.btn_google.setEnabled(not busy)
        if msg:
            self.status.setText(msg)

    def show_info(self, text: str):
        self.status.setStyleSheet("color:#22c55e; font-weight:600;")
        self.status.setText(text)

    def show_error(self, text: str):
        self.status.setStyleSheet("color:#f87171; font-weight:600;")
        self.status.setText(text)

    def remember_signup_context(self, id_token: str, email: str):
        self._last_signup_id_token = id_token
        self._last_signup_email = email

    def consume_signup_id_token(self) -> Optional[str]:
        return self._last_signup_id_token

    def last_signup_email(self) -> Optional[str]:
        return self._last_signup_email
