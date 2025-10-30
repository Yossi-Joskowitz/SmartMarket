
from __future__ import annotations
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox
)
from theme_manager import ThemeManager


class ChatView(QWidget):
    sendRequested = Signal(str, object, int)  
    appendRequested = Signal(str, str) 

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._panel: Optional[QFrame] = None
        self.chat_view: Optional[QTextEdit] = None
        self.chat_input: Optional[QLineEdit] = None
        self.force_mode_combo: Optional[QComboBox] = None
        
        # Store chat history to refresh on theme changes
        self._chat_history: list = []

        # Connect appendRequested to actual slot
        self.appendRequested.connect(self._append_chat)
        
        # Connect to theme changes
        ThemeManager.instance().themeChanged.connect(self._on_theme_changed)

        panel = QFrame(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)

        # Header
        header = QLabel("💬 SmartMarket Chat")
       
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
       
        self.chat_view.setPlaceholderText("Welcome to Smart Market Chat!\nHow can I assist you today?")

        # Bottom input row
        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 8, 0, 0)

        # Mode selector
        self.force_mode_combo = QComboBox()
        self.force_mode_combo.addItems(["auto (decide)", "db (force)", "nodb (force)"])
       
        self.force_mode_combo.setFixedWidth(130)
        self.force_mode_combo.setToolTip("Auto = let the server decide if DB is needed")

        # Input
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your question…")
       
        self.chat_input.returnPressed.connect(self._on_send_clicked)  # Enter to send

        # Send button
        send_btn = QPushButton("Send")
        send_btn.setCursor(Qt.PointingHandCursor)
       
        send_btn.clicked.connect(self._on_send_clicked)

        input_row.addWidget(self.force_mode_combo)
        input_row.addWidget(self.chat_input, stretch=1)
        input_row.addWidget(send_btn)

        # Assemble
        layout.addWidget(header)
        layout.addWidget(self.chat_view, stretch=1)
        layout.addLayout(input_row)

        panel.setLayout(layout)
        self._panel = panel

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(panel)
        self.setLayout(root)

        

    # ---- View only: formatting & UI helpers ----
    def _get_theme_colors(self):
        """Get colors appropriate for the current theme."""
        is_dark = ThemeManager.instance().theme == "dark"
        
        if is_dark:
            # Dark theme colors
            return {
                "you": "#4ADE80",      # Light green
                "assistant": "#F59E0B", # Amber/orange  
                "error": "#EF4444",    # Red
                "text": "#E5E7EB"      # Light gray
            }
        else:
            # Light theme colors
            return {
                "you": "#059669",      # Dark green
                "assistant": "#D97706", # Dark amber/orange
                "error": "#DC2626",    # Dark red  
                "text": "#374151"      # Dark gray
            }

    def _append_message_to_display(self, who: str, text: str) -> None:
        """Internal method to add a message to the display without storing in history."""
        if self.chat_view is None:
            return
        
        colors = self._get_theme_colors()
        who_color = colors["you"] if who == "You" else colors["assistant"] if who == "Assistant" else colors["error"]
        
        html = f"""
            <div style=\"margin: 6px 0;\">
                <span style=\"color:{who_color}; font-weight:600;\">{who}:</span>
                <span style=\"white-space: pre-wrap; color:{colors["text"]};\"> {text}</span>
            </div>
        """
        cursor = self.chat_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_view.setTextCursor(cursor)
        self.chat_view.insertHtml(html)
        self.chat_view.insertPlainText("\n")
        self.chat_view.moveCursor(QTextCursor.End)

    def _append_chat(self, who: str, text: str) -> None:
        """Append a line to the chat view with simple formatting."""
        # Store message in history for theme refresh
        self._chat_history.append((who, text))
        
        # Add to display
        self._append_message_to_display(who, text)

    def _on_send_clicked(self) -> None:
        # Gather input and emit event; no business logic here.
        if self.chat_input is None or self.force_mode_combo is None:
            return
        question = (self.chat_input.text() or "").strip()
        if not question:
            return
        combo_text = self.force_mode_combo.currentText()
        if combo_text.startswith("db"):
            force_mode = "db"
        elif combo_text.startswith("nodb"):
            force_mode = "nodb"
        else:
            force_mode = None
        self.sendRequested.emit(question, force_mode, 1000)

    def _refresh_chat_display(self) -> None:
        """Refresh the entire chat display with current theme colors."""
        if self.chat_view is None:
            return
        
        # Clear current content
        self.chat_view.clear()
        
        # Re-add all messages with current theme colors
        for who, text in self._chat_history:
            self._append_message_to_display(who, text)

    def _on_theme_changed(self, theme: str) -> None:
        """Handle theme changes by refreshing all chat messages with new colors."""
        self._refresh_chat_display()
    
    # Expose a way for controller to clear the input
    def clear_input(self) -> None:
        if self.chat_input is not None:
            self.chat_input.clear()
