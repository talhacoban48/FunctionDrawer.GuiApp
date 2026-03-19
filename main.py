import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QDoubleSpinBox,
    QFormLayout, QSizePolicy, QMessageBox
)
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


def parse_formula(text: str):
    """Doğal matematik notasyonunu sympy ifadesine çevirir."""
    return parse_expr(text, transformations=TRANSFORMATIONS, local_dict={'x': X})


# ---------------------------------------------------------------------------
# LaTeX önizleme için küçük matplotlib canvas
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
        self.fig.tight_layout(pad=0)

    def show_latex(self, latex_str: str):
        self.ax.clear()
        self.ax.axis('off')
        self.ax.text(
            0.5, 0.5,
            f'$f(x) = {latex_str}$',
            fontsize=13, ha='center', va='center',
            transform=self.ax.transAxes, color='#222222'
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

    # --- iç yardımcılar ---
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

    # --- dışa açık API ---
    def plot(self, func, x_min: float, x_max: float, step: float, title_latex: str = ''):
        x_inputs = np.arange(x_min, x_max + step, step)
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

        self.ax.clear()
        self.ax.plot(xs, ys, linestyle='-', linewidth=1.5, color='steelblue')
        self._style_axes()

        if title_latex:
            self.ax.set_title(f'$f(x) = {title_latex}$', fontsize=13, fontweight='bold')
        else:
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
        self.setMinimumSize(920, 580)
        self._build_ui()
        self._connect_signals()

    # --- UI oluşturma ---
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        layout.addWidget(self._left_panel())
        layout.addWidget(self._right_panel(), stretch=1)

    def _left_panel(self) -> QGroupBox:
        group = QGroupBox('Fonksiyon')
        group.setFixedWidth(300)
        vbox = QVBoxLayout(group)
        vbox.setSpacing(10)

        # Formül girişi
        vbox.addWidget(QLabel('f(x) ='))
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText('örn:  sin(4x) - 2sin(2x) / x^3')
        self.formula_input.setFont(QFont('Courier New', 12))
        self.formula_input.setMinimumHeight(36)
        vbox.addWidget(self.formula_input)

        # LaTeX önizleme
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
        btn_row.addWidget(self.draw_btn)
        btn_row.addWidget(self.clear_btn)
        vbox.addLayout(btn_row)

        vbox.addStretch()
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

    # --- sinyal bağlantıları ---
    def _connect_signals(self):
        self.formula_input.textChanged.connect(self._on_text_changed)
        self.draw_btn.clicked.connect(self._on_draw)
        self.clear_btn.clicked.connect(self._on_clear)

    # --- slot'lar ---
    def _on_text_changed(self, text: str):
        if not text.strip():
            self.preview.clear()
            return
        try:
            expr = parse_formula(text)
            self.preview.show_latex(latex(expr))
        except Exception:
            self.preview.show_error()

    def _on_draw(self):
        text = self.formula_input.text().strip()
        if not text:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen bir fonksiyon girin.')
            return

        x_min = self.min_spin.value()
        x_max = self.max_spin.value()
        if x_min >= x_max:
            QMessageBox.warning(self, 'Uyarı', 'Min değeri Max değerinden küçük olmalıdır.')
            return

        try:
            expr = parse_formula(text)
            func = lambdify(X, expr, modules=['numpy'])
            self.plot_canvas.plot(
                func, x_min, x_max,
                self.step_spin.value(),
                title_latex=latex(expr)
            )
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Fonksiyon çizilemedi:\n{e}')

    def _on_clear(self):
        self.formula_input.clear()
        self.plot_canvas.clear()


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
