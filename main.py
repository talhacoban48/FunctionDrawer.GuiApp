import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QDoubleSpinBox,
    QFormLayout, QSizePolicy, QMessageBox, QScrollArea, QFrame
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from sympy import symbols, latex, lambdify
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor
)


TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)
X = symbols('x')

COLORS = [
    'steelblue', 'darkorange', 'seagreen', '#cc3333',
    '#9b59b6', '#e67e22', '#1abc9c', '#e91e63',
]


def parse_formula(text: str):
    return parse_expr(text, transformations=TRANSFORMATIONS, local_dict={'x': X})


# ---------------------------------------------------------------------------
# Tek bir formül satırı
# ---------------------------------------------------------------------------
class FormulaRow(QWidget):
    text_changed = pyqtSignal(object, str)   # (self, text)
    remove_requested = pyqtSignal(object)    # (self)

    def __init__(self, color: str, index: int, parent=None):
        super().__init__(parent)
        self.color = color

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        # Renk göstergesi
        dot = QFrame()
        dot.setFixedSize(14, 14)
        dot.setStyleSheet(
            f'background-color: {color}; border-radius: 7px;'
        )
        row.addWidget(dot)

        # Formül girişi
        self.input = QLineEdit()
        self.input.setPlaceholderText(f'f{index}(x) =')
        self.input.setFont(QFont('Courier New', 11))
        self.input.setMinimumHeight(32)
        row.addWidget(self.input, stretch=1)

        # Sil butonu
        remove_btn = QPushButton('×')
        remove_btn.setFixedSize(28, 28)
        remove_btn.setStyleSheet('color: #cc3333; font-size: 16px; border: none;')
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        row.addWidget(remove_btn)

        self.input.textChanged.connect(lambda t: self.text_changed.emit(self, t))

    def text(self) -> str:
        return self.input.text().strip()

    def set_index(self, index: int):
        self.input.setPlaceholderText(f'f{index}(x) =')


# ---------------------------------------------------------------------------
# LaTeX önizleme
# ---------------------------------------------------------------------------
class PreviewCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(3, 0.7), facecolor='#f8f8f8')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setFixedHeight(55)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.axis('off')

    def show_latex(self, latex_str: str, color: str = '#222222'):
        self.ax.clear()
        self.ax.axis('off')
        self.ax.text(
            0.5, 0.5,
            f'$f(x) = {latex_str}$',
            fontsize=13, ha='center', va='center',
            transform=self.ax.transAxes, color=color
        )
        self.draw()

    def show_error(self):
        self.ax.clear()
        self.ax.axis('off')
        self.ax.text(
            0.5, 0.5, 'Geçersiz ifade',
            fontsize=11, ha='center', va='center',
            transform=self.ax.transAxes, color='#cc3333'
        )
        self.draw()

    def clear(self):
        self.ax.clear()
        self.ax.axis('off')
        self.draw()


# ---------------------------------------------------------------------------
# Ana grafik canvas
# ---------------------------------------------------------------------------
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(facecolor='white')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax = self.fig.add_subplot(111)
        self._draw_empty()

    def _style_axes(self):
        self.ax.axhline(y=0, color='#cc2222', linewidth=0.8)
        self.ax.axvline(x=0, color='#cc2222', linewidth=0.8)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('f(x)', fontsize=12)

    def _draw_empty(self):
        self.ax.clear()
        self._style_axes()
        self.ax.set_title('Fonksiyon Grafiği', fontsize=14, fontweight='bold')
        self.fig.tight_layout()
        self.draw()

    def plot_all(self, functions: list, x_min: float, x_max: float, step: float):
        """functions: list of (callable, latex_str, color)"""
        x_inputs = np.arange(x_min, x_max + step, step)
        self.ax.clear()

        for func, latex_str, color in functions:
            xs, ys = [], []
            for x in x_inputs:
                try:
                    xr = float(np.round(x, 6))
                    yr = float(func(xr))
                    if np.isfinite(yr):
                        xs.append(xr)
                        ys.append(yr)
                except Exception:
                    pass
            self.ax.plot(xs, ys, linestyle='-', linewidth=1.5,
                         color=color, label=f'$f(x)={latex_str}$')

        self._style_axes()
        if functions:
            self.ax.legend(fontsize=10, loc='best')
        self.ax.set_title('Fonksiyon Grafiği', fontsize=14, fontweight='bold')
        self.fig.tight_layout()
        self.draw()

    def clear(self):
        self._draw_empty()


# ---------------------------------------------------------------------------
# Ana pencere
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Function Drawer')
        self.setMinimumSize(960, 580)
        self._rows: list[FormulaRow] = []
        self._build_ui()
        self._add_row()   # Başlangıçta bir satır

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(self._left_panel())
        layout.addWidget(self._right_panel(), stretch=1)

    # --- sol panel ---
    def _left_panel(self) -> QGroupBox:
        group = QGroupBox('Fonksiyonlar')
        group.setFixedWidth(360)
        vbox = QVBoxLayout(group)
        vbox.setSpacing(10)

        # Kaydırılabilir formül listesi
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            scroll.horizontalScrollBarPolicy() if False else 0x1  # off
        )

        self._rows_widget = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setSpacing(6)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.addStretch()
        scroll.setWidget(self._rows_widget)
        scroll.setMinimumHeight(140)
        vbox.addWidget(scroll)

        # Fonksiyon ekle butonu
        add_btn = QPushButton('+ Fonksiyon Ekle')
        add_btn.clicked.connect(self._add_row)
        vbox.addWidget(add_btn)

        # Önizleme
        vbox.addWidget(QLabel('Önizleme:'))
        self.preview = PreviewCanvas(self)
        vbox.addWidget(self.preview)

        # Min / Max / Step
        form_widget = QWidget()
        form = QFormLayout(form_widget)
        form.setSpacing(8)
        self.min_spin = self._make_spin(-10, -1000, 1000, step=1.0)
        self.max_spin = self._make_spin(10, -1000, 1000, step=1.0)
        self.step_spin = self._make_spin(0.01, 0.0001, 10.0, step=0.01, decimals=4)
        form.addRow('Min:', self.min_spin)
        form.addRow('Max:', self.max_spin)
        form.addRow('Adım:', self.step_spin)
        vbox.addWidget(form_widget)

        # Butonlar
        btn_row = QHBoxLayout()
        self.draw_btn = QPushButton('Çiz')
        self.draw_btn.setMinimumHeight(36)
        self.draw_btn.setDefault(True)
        self.clear_btn = QPushButton('Temizle')
        self.clear_btn.setMinimumHeight(36)
        self.draw_btn.clicked.connect(self._on_draw)
        self.clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(self.draw_btn)
        btn_row.addWidget(self.clear_btn)
        vbox.addLayout(btn_row)

        return group

    def _right_panel(self) -> QGroupBox:
        group = QGroupBox('Grafik')
        vbox = QVBoxLayout(group)
        vbox.setContentsMargins(6, 6, 6, 6)
        self.plot_canvas = PlotCanvas(self)
        vbox.addWidget(self.plot_canvas)
        return group

    @staticmethod
    def _make_spin(default, lo, hi, step=1.0, decimals=2) -> QDoubleSpinBox:
        sb = QDoubleSpinBox()
        sb.setRange(lo, hi)
        sb.setValue(default)
        sb.setSingleStep(step)
        sb.setDecimals(decimals)
        return sb

    # --- satır yönetimi ---
    def _add_row(self):
        index = len(self._rows) + 1
        color = COLORS[(index - 1) % len(COLORS)]
        row = FormulaRow(color=color, index=index, parent=self)
        row.text_changed.connect(self._on_row_text_changed)
        row.remove_requested.connect(self._remove_row)
        self._rows.append(row)
        # stretch'ten önce ekle
        self._rows_layout.insertWidget(self._rows_layout.count() - 1, row)

    def _remove_row(self, row: FormulaRow):
        if len(self._rows) == 1:
            row.input.clear()
            return
        self._rows.remove(row)
        row.setParent(None)
        row.deleteLater()
        for i, r in enumerate(self._rows):
            r.set_index(i + 1)

    # --- slot'lar ---
    def _on_row_text_changed(self, row: FormulaRow, text: str):
        if not text.strip():
            self.preview.clear()
            return
        try:
            expr = parse_formula(text)
            self.preview.show_latex(latex(expr), color=row.color)
        except Exception:
            self.preview.show_error()

    def _on_draw(self):
        x_min = self.min_spin.value()
        x_max = self.max_spin.value()
        if x_min >= x_max:
            QMessageBox.warning(self, 'Uyarı', 'Min değeri Max değerinden küçük olmalıdır.')
            return

        functions = []
        errors = []
        for row in self._rows:
            text = row.text()
            if not text:
                continue
            try:
                expr = parse_formula(text)
                func = lambdify(X, expr, modules=['numpy'])
                functions.append((func, latex(expr), row.color))
            except Exception as e:
                errors.append(f'  "{text}" → {e}')

        if errors:
            QMessageBox.critical(self, 'Hata', 'Bazı fonksiyonlar çizilemedi:\n' + '\n'.join(errors))

        if not functions:
            QMessageBox.warning(self, 'Uyarı', 'Çizilecek geçerli bir fonksiyon girilmedi.')
            return

        self.plot_canvas.plot_all(functions, x_min, x_max, self.step_spin.value())

    def _on_clear(self):
        for row in self._rows:
            row.input.clear()
        self.plot_canvas.clear()
        self.preview.clear()


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
