from PyQt6.QtWidgets import QListWidget
from PyQt6.QtGui import QPainter, QFont, QColor
from PyQt6.QtCore import Qt

class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        self._placeholder_font = QFont("Arial", 12)
        self._placeholder_color = QColor("#7f8c8d")
        self._placeholder_text = "Drag and drop files here"

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0:
            painter = QPainter(self.viewport())
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(self._placeholder_color)
            painter.setFont(self._placeholder_font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._placeholder_text)
            painter.restore()