"""
HeroSense - Corner Overlay (PyQt6)

  - Enemy comp type with color coding
  - Heroes to play (green)
  - Heroes to avoid (red)

Call from capture.py:
    from overlay import show_overlay
    show_overlay(analysis)

Or test standalone:
    python overlay.py

Requires: pip install PyQt6
"""

import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import QCoreApplication
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True) if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling') else None

# Theme 

COMP_COLORS = {
    "dive":    "#00cfff",
    "poke":    "#f5c400",
    "brawl":   "#ff6b35",
    "rush":    "#cc44ff",
    "disrupt": "#ff4466",
    "mixed":   "#aaaaaa",
}

BG_COLOR        = "#0d0f14"
BG_CARD         = "#161921"
BORDER_COLOR    = "#2a2d3a"
TEXT_PRIMARY    = "#f0f2ff"
TEXT_DIM        = "#6b7080"
GREEN           = "#39d98a"
RED             = "#ff5c6a"
AUTO_CLOSE_MS   = 20000   # auto-hide after 20 seconds (0 to disable)


# Signal bridge (thread-safe updates) 

class OverlaySignals(QObject):
    update = pyqtSignal(dict)
    close  = pyqtSignal()


# Main widget 

class OW2Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = OverlaySignals()
        self.signals.update.connect(self._update_content)
        self.signals.close.connect(self.hide)
        self._build_ui()
        self._position_window()

    # Window setup 

    def _build_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(280)
        self.setMaximumWidth(400)

        # Outer container with border
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setStyleSheet(f"""
            QFrame#card {{
                background: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
            }}
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(14, 12, 14, 14)
        card_layout.setSpacing(10)

        # Header row 
        header = QHBoxLayout()

        title_layout = QHBoxLayout()
        title_layout.setSpacing(0)
        title_hero = QLabel("HERO")
        title_hero.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        title_hero.setStyleSheet(f"color: {TEXT_DIM}; letter-spacing: 2px;")
        title_sense = QLabel("SENSE")
        title_sense.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        title_sense.setStyleSheet("color: #cc44ff; letter-spacing: 2px;")
        title_layout.addWidget(title_hero)
        title_layout.addWidget(title_sense)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(18, 18)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_DIM};
                border: none;
                font-size: 11px;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
        """)
        close_btn.clicked.connect(self.hide)

        header.addLayout(title_layout)
        header.addStretch()
        header.addWidget(close_btn)
        card_layout.addLayout(header)

        # Divider 
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {BORDER_COLOR};")
        card_layout.addWidget(divider)

        # Comp type badge 
        comp_row = QHBoxLayout()
        comp_label = QLabel("ENEMY COMP")
        comp_label.setFont(QFont("Consolas", 8))
        comp_label.setStyleSheet(f"color: {TEXT_DIM};")

        self.comp_badge = QLabel("—")
        self.comp_badge.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.comp_badge.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.comp_badge.setStyleSheet(f"color: {TEXT_PRIMARY};")

        comp_row.addWidget(comp_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        comp_row.addStretch()
        comp_row.addWidget(self.comp_badge, alignment=Qt.AlignmentFlag.AlignVCenter)
        card_layout.addLayout(comp_row)

        # Description
        self.desc_label = QLabel("")
        self.desc_label.setFont(QFont("Segoe UI", 8))
        self.desc_label.setStyleSheet(f"color: {TEXT_DIM};")
        self.desc_label.setWordWrap(True)
        card_layout.addWidget(self.desc_label)

        # Play section 
        play_header = QLabel("PLAY")
        play_header.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        play_header.setStyleSheet(f"color: {GREEN};")
        card_layout.addWidget(play_header)

        self.play_label = QLabel("—")
        self.play_label.setFont(QFont("Segoe UI", 9))
        self.play_label.setStyleSheet(f"color: {TEXT_PRIMARY}; padding-left: 4px;")
        self.play_label.setWordWrap(True)
        card_layout.addWidget(self.play_label)

        # Avoid section 
        avoid_header = QLabel("AVOID")
        avoid_header.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        avoid_header.setStyleSheet(f"color: {RED};")
        card_layout.addWidget(avoid_header)

        self.avoid_label = QLabel("—")
        self.avoid_label.setFont(QFont("Segoe UI", 9))
        self.avoid_label.setStyleSheet(f"color: {TEXT_PRIMARY}; padding-left: 4px;")
        self.avoid_label.setWordWrap(True)
        card_layout.addWidget(self.avoid_label)

        outer.addWidget(self.card)

    def _position_window(self):
        """Snap to bottom-right corner of the screen."""
        screen = QApplication.primaryScreen().availableGeometry()
        self.adjustSize()
        x = screen.right()  - self.width()  - 20
        y = screen.bottom() - self.height() - 20
        self.move(x, y)

    # Content update 

    def _update_content(self, analysis: dict):
        comp        = analysis.get("enemy_comp", "mixed")
        description = analysis.get("description", "")
        play        = analysis.get("play",  [])
        avoid       = analysis.get("avoid", [])

        color = COMP_COLORS.get(comp, "#aaaaaa")

        self.comp_badge.setText(comp.upper())
        self.comp_badge.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.card.setStyleSheet(f"""
            QFrame#card {{
                background: {BG_COLOR};
                border: 1px solid {color};
                border-radius: 10px;
            }}
        """)

        self.desc_label.setText(description)

        # Format hero lists — title case, comma separated
        def fmt(heroes): return ",  ".join(h.title() for h in heroes[:6]) if heroes else "None"
        self.play_label.setText(fmt(play))
        self.avoid_label.setText(fmt(avoid))

        self.adjustSize()
        self._position_window()
        self.show()
        self.raise_()

        # Auto-close timer
        if AUTO_CLOSE_MS > 0:
            QTimer.singleShot(AUTO_CLOSE_MS, self.hide)

    # Drag to move 

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)


# Public API 

_app: QApplication | None = None
_overlay: OW2Overlay | None = None


def _ensure_app():
    global _app, _overlay
    if _app is None:
        _app = QApplication.instance() or QApplication(sys.argv)
        _overlay = OW2Overlay()


def show_overlay(analysis: dict):
    """
    Thread-safe. Call from any thread — works from capture.py background thread.
    """
    _ensure_app()
    _overlay.signals.update.emit(analysis)


def run_overlay_loop():
    """
    Blocking — starts the Qt event loop.
    Call this once from your main thread (capture.py already does this).
    """
    _ensure_app()
    _app.exec()


# test 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = OW2Overlay()

    test_cases = [
        {
            "enemy_comp":  "dive",
            "description": "High-mobility flankers targeting your backline. Use CC and hitscan to shut them down.",
            "play":  ["cassidy", "soldier76", "ana", "brigitte", "torbjorn", "sigma"],
            "avoid": ["widowmaker", "hanzo", "symmetra"],
        },
        {
            "enemy_comp":  "poke",
            "description": "Long-range sustained damage. Get in their face or out-range them.",
            "play":  ["winston", "dva", "genji", "tracer", "lucio", "pharah"],
            "avoid": ["reinhardt", "roadhog", "torbjorn"],
        },
        {
            "enemy_comp":  "brawl",
            "description": "Short-range high-sustain. Keep distance, poke them out, burst them down.",
            "play":  ["bastion", "pharah", "junkrat", "soldier76", "ashe", "zenyatta"],
            "avoid": ["reaper", "moira", "symmetra"],
        },
        {
            "enemy_comp":  "rush",
            "description": "Fast all-in aggression. Slow them with CC and area denial before they engage.",
            "play":  ["mei", "junkrat", "cassidy", "ana", "sigma", "orisa"],
            "avoid": ["widowmaker", "zenyatta", "bastion"],
        },
        {
            "enemy_comp":  "disrupt",
            "description": "Heavy CC and off-angles. Stay grouped, focus targets fast, use cleanse supports.",
            "play":  ["soldier76", "cassidy", "lucio", "kiriko", "reinhardt", "zarya"],
            "avoid": ["widowmaker", "hanzo", "lifeweaver"],
        },
        {
            "enemy_comp":  "mixed",
            "description": "No clear archetype. Play to your team's strengths.",
            "play":  ["soldier76", "ana", "lucio", "dva", "sigma"],
            "avoid": [],
        },
    ]

    current = [0]

    def cycle():
        overlay.signals.update.emit(test_cases[current[0] % len(test_cases)])
        current[0] += 1
        QTimer.singleShot(4000, cycle)

    cycle()
    sys.exit(app.exec())