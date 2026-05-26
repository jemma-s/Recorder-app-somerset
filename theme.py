"""
theme.py
--------
Applies a custom theme to the app.
Falls back to pyqtdarktheme's light theme if anything goes wrong.

Usage (in main.py):
    from theme import apply_theme
    apply_theme(app)
"""

from PyQt6.QtWidgets import QApplication, QTableWidget


# ---------------------------------------------------------------------------
# Colour palette — edit these to change the whole theme
# ---------------------------------------------------------------------------

COLORS = {
    "primary":          "#2563eb",   # main blue — buttons, accents
    "primary_hover":    "#1d4ed8",   # button hover
    "primary_text":     "#ffffff",   # text on primary-coloured backgrounds
    "primary_disabled": "#93c5fd",   # disabled button face

    "bg":               "#f8fafc",   # main window background
    "bg_surface":       "#ffffff",   # cards, tables, inputs
    "bg_hover":         "#f1f5f9",   # row hover, subtle highlights

    "border":           "#cbd5e1",   # input/table borders
    "border_focus":     "#2563eb",   # focused input border

    "text_primary":     "#0f172a",   # headings, important labels
    "text_secondary":   "#475569",   # helper text, subtitles
    "text_disabled":    "#94a3b8",   # disabled widget text

    "warning":          "#d97706",   # warning labels
    "error":            "#dc2626",   # error labels
    "success":          "#16a34a",   # success labels

    "header_bg":        "#1e3a5f",   # table header background
    "header_text":      "#ffffff",   # table header text
    "row_alt":          "#f1f5f9",   # alternating table row
}

# ---------------------------------------------------------------------------
# QSS template — references the palette above
# ---------------------------------------------------------------------------

QSS = """
/* ── Global ── */
QWidget {{
    background-color: {bg};
    color: {text_primary};
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

/* ── Main window / dialogs ── */
QMainWindow, QDialog {{
    background-color: {bg};
}}

/* ── Labels ── */
QLabel {{
    background-color: transparent;
    color: {text_primary};
}}

/* ── Buttons ── */
QPushButton {{
    background-color: {primary};
    color: {primary_text};
    border: none;
    border-radius: 6px;
    padding: 7px 18px;
    font-weight: 700;
}}
QPushButton:hover {{
    background-color: {primary_hover};
}}
QPushButton:pressed {{
    background-color: {primary};
    padding-top: 8px;
    padding-bottom: 6px;
}}
QPushButton:disabled {{
    background-color: {primary_disabled};
    color: {primary_text};
}}

/* ── ComboBox ── */
QComboBox {{
    background-color: {bg_surface};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 5px;
    padding: 5px 10px;
    min-height: 28px;
}}
QComboBox:focus {{
    border-color: {border_focus};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}
QComboBox QAbstractItemView {{
    background-color: {bg_surface};
    color: {text_primary};
    border: 1px solid {border};
    selection-background-color: {primary};
    selection-color: {primary_text};
    outline: none;
}}

/* ── Table ── */
QTableWidget {{
    background-color: {bg_surface};
    alternate-background-color: {row_alt};
    gridline-color: {border};
    border: 1px solid {border};
    border-radius: 6px;
    min-height: 275px;
}}
QTableWidget::item {{
    padding: 4px 8px;
    color: {text_primary};
}}
QTableWidget::item:selected {{
    background-color: {primary};
    color: {primary_text};
}}
QTableWidget::item:hover {{
    background-color: {bg_hover};
}}
QHeaderView::section {{
    background-color: {header_bg};
    color: {header_text};
    padding: 6px 8px;
    border: none;
    border-right: 1px solid {border};
    font-weight: 600;
}}
QHeaderView::section:last {{
    border-right: none;
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: {bg};
    width: 8px;
    margin: 0;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {border};
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: {text_secondary};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {bg};
    height: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal {{
    background: {border};
    min-width: 20px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {text_secondary};
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── Tab bar ── */
QTabBar::tab {{
    background-color: {bg};
    color: {text_secondary};
    border: 1px solid {border};
    border-bottom: none;
    padding: 7px 16px;
    margin-right: 2px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}}
QTabBar::tab:selected {{
    background-color: {bg_surface};
    color: {text_primary};
    font-weight: 600;
    border-bottom: 2px solid {primary};
}}
QTabBar::tab:hover:!selected {{
    background-color: {bg_hover};
    color: {text_primary};
}}
QTabWidget::pane {{
    border: 1px solid {border};
    background-color: {bg_surface};
}}

/* ── Message boxes ── */
QMessageBox {{
    background-color: {bg_surface};
}}
QMessageBox QLabel {{
    color: {text_primary};
    min-width: 280px;
}}

/* ── File dialog ── */
QFileDialog {{
    background-color: {bg};
}}

/* ── Status / helper labels via object name ── */
QLabel#warningLabel {{
    color: {warning};
    font-weight: bold;
}}
QLabel#errorLabel {{
    color: {error};
    font-weight: bold;
}}
QLabel#successLabel {{
    color: {success};
    font-weight: bold;
}}
QLabel#titleLabel {{
    font-size: 18px;
    font-weight: bold;
    color: {text_primary};
}}
QLabel#subtitleLabel {{
    font-size: 13px;
    color: {text_secondary};
}}
"""

class ScrollFreeTable(QTableWidget):
    """Making tables not be scrollable by using the mouse. To scroll, you have to use the scroll bar """
    def wheelEvent(self, event):
        event.ignore()

def _build_qss() -> str:
    """Interpolate the colour palette into the QSS template."""
    return QSS.format(**COLORS)


def apply_theme(app: QApplication) -> None:
    """Apply the custom theme to the app, with qdarktheme light as fallback.

    Parameters
    ----------
    app : QApplication
        The running QApplication instance.
    """
    try:
        app.setStyleSheet(_build_qss())
        print("[theme] Custom theme applied.")
    except Exception as exc:
        print(f"[theme] Custom theme failed ({exc}), falling back to qdarktheme light.")
        _apply_fallback(app)


def _apply_fallback(app: QApplication) -> None:
    """Apply qdarktheme light as a fallback."""
    try:
        import qdarktheme
        qdarktheme.setup_theme("light")
        print("[theme] qdarktheme light fallback applied.")
    except ImportError:
        print("[theme] qdarktheme not installed — no fallback available. Run: pip install pyqtdarktheme")
    except Exception as exc:
        print(f"[theme] Fallback also failed: {exc}")
