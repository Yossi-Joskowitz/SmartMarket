from PySide6.QtWidgets import QVBoxLayout, QLabel, QSplashScreen
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation, QRect
from PySide6.QtGui import QPainter, QPixmap, QLinearGradient, QColor


class SplashScreen(QSplashScreen):
    """
    A frameless, dark splash screen with a centered title and a simple
    text-based spinner that updates every 200ms while the app loads.
    """

    def __init__(self):
        super().__init__()

        # ----- Window basics -----
        self.setFixedSize(400, 300)                       # Fixed splash size
        self.setWindowFlag(Qt.FramelessWindowHint, True)  # No title bar / borders
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # ----- Background (painted pixmap) -----
        # Create a gradient dark background and set it as the splash pixmap.
        bg = QPixmap(self.width(), self.height())
        bg.fill(Qt.transparent)
        painter = QPainter(bg)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#1E1E1E"))
        grad.setColorAt(1.0, QColor("#2B2B2B"))
        painter.fillRect(bg.rect(), grad)
        painter.end()
        self.setPixmap(bg)

        # ----- Content layout attached to THIS widget -----
        layout = QVBoxLayout(self)               # <— attach layout to splash itself
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # ----- Title label -----
        self.title = QLabel("AI Retail Dashboard", self)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
        """)
        layout.addWidget(self.title)

        # ----- Spinner label (text-based anim) -----
        self.spinner = QLabel("●", self)
        self.spinner.setAlignment(Qt.AlignCenter)
        self.spinner.setStyleSheet("""
            QLabel {
                color: #00E0FF;
                font-size: 48px;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.spinner)

        # ----- Optional subtle attention animation (scale via geometry) -----
        # (Not required for the text-rotation effect, but looks nice.)
        self._pulse_anim = QPropertyAnimation(self.spinner, b"geometry", self)
        self._pulse_anim.setDuration(900)
        self._pulse_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self._pulse_anim.setLoopCount(-1)  # infinite
        # Geometry will be set after showEvent when we know final widget rect.

        # ----- Timer for spinner state changes -----
        self._spin_state = 0
        self._states = ["●", "◐", "◑", "◒"]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_spinner)
        self._timer.start(280)  # every 280ms

    def showEvent(self, event):
        """
        Start the subtle pulse animation once we know the widget's geometry.
        """
        super().showEvent(event)
        # Define a gentle geometry pulse around current rect:
        r = self.spinner.geometry()
        inset = 3
        start_rect = QRect(r.adjusted(+inset, +inset, -inset, -inset))
        end_rect   = QRect(r.adjusted(-inset, -inset, +inset, +inset))
        self._pulse_anim.setStartValue(start_rect)
        self._pulse_anim.setEndValue(end_rect)
        self._pulse_anim.start()

    def _update_spinner(self):
        """
        Rotate through a set of unicode symbols to simulate a loading spinner.
        """
        self.spinner.setText(self._states[self._spin_state % len(self._states)])
        self._spin_state += 1
