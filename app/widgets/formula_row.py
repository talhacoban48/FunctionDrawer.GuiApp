from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFrame
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from app.constants import asset


class FormulaRow(QWidget):
    text_changed    = pyqtSignal(object, str)
    remove_requested = pyqtSignal(object)

    def __init__(self, color: str, index: int, parent=None):
        super().__init__(parent)
        self.color = color

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        dot = QFrame()
        dot.setFixedSize(14, 14)
        dot.setStyleSheet(f'background-color: {color}; border-radius: 7px;')
        layout.addWidget(dot)

        self.input = QLineEdit()
        self.input.setPlaceholderText(f'f{index}(x) =')
        self.input.setFont(QFont('Courier New', 11))
        self.input.setMinimumHeight(32)
        layout.addWidget(self.input, stretch=1)

        remove_btn = QPushButton()
        remove_btn.setIcon(QIcon(asset('cancel.ico')))
        remove_btn.setFixedSize(28, 28)
        remove_btn.setStyleSheet('border: none;')
        remove_btn.setToolTip('Sil')
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_btn)

        self.input.textChanged.connect(lambda t: self.text_changed.emit(self, t))

    def text(self) -> str:
        return self.input.text().strip()

    def set_index(self, index: int):
        self.input.setPlaceholderText(f'f{index}(x) =')
