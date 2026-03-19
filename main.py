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
from PyQt5.QtGui import QFont, QIcon
from sympy import symbols, latex, lambdify, diff, integrate, N
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
    text_changed = pyqtSignal(object, str)
    remove_requested = pyqtSignal(object)

    def __init__(self, color: str, index: int, parent=None):
        super().__init__(parent)
        self.color = color

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        dot = QFrame()
        dot.setFixedSize(14, 14)
        dot.setStyleSheet(f'background-color: {color}; border-radius: 7px;')
        row.addWidget(dot)

        self.input = QLineEdit()
        self.input.setPlaceholderText(f'f{index}(x) =')
        self.input.setFont(QFont('Courier New', 11))
        self.input.setMinimumHeight(32)
        row.addWidget(self.input, stretch=1)

        remove_btn = QPushButton()
        remove_btn.setIcon(QIcon('assets/cancel.ico'))
        remove_btn.setFixedSize(28, 28)
        remove_btn.setStyleSheet('border: none;')
        remove_btn.setToolTip('Sil')
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        row.addWidget(remove_btn)

        self.input.textChanged.connect(lambda t: self.text_changed.emit(self, t))

    def text(self) -> str:
        return self.input.text().strip()

    def set_index(self, index: int):
        self.input.setPlaceholderText(f'f{index}(x) =')


# ---------------------------------------------------------------------------
# LaTeX önizleme (tek satır)
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
        self.ax.text(0.5, 0.5, f'$f(x) = {latex_str}$',
                     fontsize=13, ha='center', va='center',
                     transform=self.ax.transAxes, color=color)
        self.draw()

    def show_error(self):
        self.ax.clear()
        self.ax.axis('off')
        self.ax.text(0.5, 0.5, 'Geçersiz ifade',
                     fontsize=11, ha='center', va='center',
                     transform=self.ax.transAxes, color='#cc3333')
        self.draw()

    def clear(self):
        self.ax.clear()
        self.ax.axis('off')
        self.draw()


# ---------------------------------------------------------------------------
# Hesaplama sonuçları (çok satır LaTeX)
# ---------------------------------------------------------------------------
class ResultsCanvas(FigureCanvas):
    LINE_H = 42   # piksel / satır

    def __init__(self, parent=None):
        self.fig = Figure(facecolor='#f5f5f5')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(0)

    def show(self, lines: list):
        """lines: [(label_str, latex_body, color), ...]
           label_str  → sol sütun (renk + etiket, ör. "f₁'(x) =")
           latex_body → sağ sütun, LaTeX; None ise plain text olarak göster
        """
        self.fig.clear()
        n = len(lines)
        if n == 0:
            self.setFixedHeight(0)
            self.draw()
            return

        h = n * self.LINE_H + 8
        self.setFixedHeight(h)
        self.fig.set_size_inches(4, h / 96)

        ax = self.fig.add_axes([0.01, 0, 0.99, 1])
        ax.axis('off')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        for i, (label, body, color) in enumerate(lines):
            y = 1 - (i + 0.5) / n
            ax.text(0.01, y, label, fontsize=9, ha='left', va='center',
                    color=color, fontweight='bold')
            if body is not None:
                ax.text(0.32, y, f'${body}$', fontsize=10, ha='left', va='center',
                        color='#1a1a1a')

        self.fig.tight_layout(pad=0.1)
        self.draw()

    def clear_results(self):
        self.fig.clear()
        self.setFixedHeight(0)
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
        self._base: list   = []   # (func, latex_str, color)
        self._derivs: list = []   # (func, latex_str, color)
        self._fills: list  = []   # (func, a, b, color)
        self._x_range = (-10.0, 10.0, 0.01)
        self._draw_empty()

    def _style_axes(self):
        self.ax.axhline(y=0, color='#cc2222', linewidth=0.8)
        self.ax.axvline(x=0, color='#cc2222', linewidth=0.8)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('f(x)', fontsize=12)
        for spine in self.ax.spines.values():
            spine.set_visible(False)

    def _draw_empty(self):
        self.ax.clear()
        self._style_axes()
        self.ax.set_title('Fonksiyon Grafiği', fontsize=14, fontweight='bold')
        self.fig.tight_layout()
        self.draw()

    @staticmethod
    def _safe_eval(func, x_arr):
        """Vektörel hesapla, sonsuz/NaN noktaları maskele."""
        try:
            ys = np.asarray(func(x_arr), dtype=float)
            mask = np.isfinite(ys)
            return x_arr[mask], ys[mask]
        except Exception:
            xs, ys = [], []
            for x in x_arr:
                try:
                    y = float(func(float(x)))
                    if np.isfinite(y):
                        xs.append(float(x))
                        ys.append(y)
                except Exception:
                    pass
            return np.array(xs), np.array(ys)

    def _redraw(self):
        x_min, x_max, step = self._x_range
        x_arr = np.arange(x_min, x_max + step, step)
        self.ax.clear()

        for func, latex_str, color in self._base:
            xs, ys = self._safe_eval(func, x_arr)
            self.ax.plot(xs, ys, '-', linewidth=1.5, color=color,
                         label=f'$f(x)={latex_str}$')

        for func, latex_str, color in self._derivs:
            xs, ys = self._safe_eval(func, x_arr)
            self.ax.plot(xs, ys, '--', linewidth=1.2, color=color, alpha=0.85,
                         label=f"$f'(x)={latex_str}$")

        for func, a, b, color in self._fills:
            fill_x = np.linspace(a, b, 3000)
            _, fill_y = self._safe_eval(func, fill_x)
            fill_x2, _ = self._safe_eval(func, fill_x)
            self.ax.fill_between(fill_x2, fill_y, 0,
                                 alpha=0.25, color=color,
                                 label=f'Alan $[{a:.3g},\\ {b:.3g}]$')

        self._style_axes()
        has_labels = self._base or self._derivs or self._fills
        if has_labels:
            self.ax.legend(fontsize=10, loc='best')
        self.ax.set_title('Fonksiyon Grafiği', fontsize=14, fontweight='bold')
        self.fig.tight_layout()
        self.draw()

    # --- dışa açık API ---
    def plot_all(self, functions: list, x_min: float, x_max: float, step: float):
        self._base = functions
        self._derivs = []
        self._fills = []
        self._x_range = (x_min, x_max, step)
        self._redraw()

    def add_derivatives(self, deriv_funcs: list):
        """deriv_funcs: [(func, latex_str, color)]"""
        self._derivs = deriv_funcs
        self._redraw()

    def add_fills(self, fill_infos: list):
        """fill_infos: [(func, a, b, color)]"""
        self._fills = fill_infos
        self._redraw()

    def clear_extras(self):
        self._derivs = []
        self._fills = []
        self._redraw()

    def clear(self):
        self._base = []
        self._derivs = []
        self._fills = []
        self._x_range = (-10.0, 10.0, 0.01)
        self._draw_empty()


# ---------------------------------------------------------------------------
# Ana pencere
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Function Drawer')
        self.setWindowIcon(QIcon('assets/favicon.ico'))
        self.setMinimumSize(960, 640)
        self._rows: list[FormulaRow] = []
        self._build_ui()
        self._add_row()

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
        group.setFixedWidth(420)

        # Tüm sol panel içeriğini scroll'a sar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        vbox = QVBoxLayout(inner)
        vbox.setSpacing(10)
        vbox.setContentsMargins(4, 4, 4, 4)

        # --- Formül listesi ---
        self._fn_scroll = QScrollArea()
        self._fn_scroll.setWidgetResizable(True)
        self._fn_scroll.setFrameShape(QFrame.NoFrame)
        self._fn_scroll.setHorizontalScrollBarPolicy(0x1)   # off

        self._rows_widget = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setSpacing(6)
        self._rows_layout.setContentsMargins(0, 2, 0, 2)
        self._fn_scroll.setWidget(self._rows_widget)
        vbox.addWidget(self._fn_scroll)

        add_btn = QPushButton(' Fonksiyon Ekle')
        add_btn.setIcon(QIcon('assets/add.ico'))
        add_btn.clicked.connect(self._add_row)
        vbox.addWidget(add_btn)

        # --- Önizleme ---
        vbox.addWidget(QLabel('Önizleme:'))
        self.preview = PreviewCanvas(self)
        vbox.addWidget(self.preview)

        # --- Min / Max / Step ---
        form_widget = QWidget()
        form = QFormLayout(form_widget)
        form.setSpacing(8)
        self.min_spin  = self._make_spin(-10,   -1000, 1000, step=1.0)
        self.max_spin  = self._make_spin( 10,   -1000, 1000, step=1.0)
        self.step_spin = self._make_spin(0.01, 0.0001, 10.0, step=0.01, decimals=4)
        form.addRow('Min:',  self.min_spin)
        form.addRow('Max:',  self.max_spin)
        form.addRow('Adım:', self.step_spin)
        vbox.addWidget(form_widget)

        # --- Çiz / Temizle ---
        btn_row = QHBoxLayout()
        self.draw_btn  = QPushButton(' Çiz')
        self.draw_btn.setIcon(QIcon('assets/search.ico'))
        self.draw_btn.setMinimumHeight(36)
        self.draw_btn.setDefault(True)
        self.clear_btn = QPushButton(' Temizle')
        self.clear_btn.setIcon(QIcon('assets/cancel.ico'))
        self.clear_btn.setMinimumHeight(36)
        self.draw_btn.clicked.connect(self._on_draw)
        self.clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(self.draw_btn)
        btn_row.addWidget(self.clear_btn)
        vbox.addLayout(btn_row)

        # ── Ayraç ──────────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        vbox.addWidget(sep)

        # --- Hesaplamalar: tek satır ---
        calc_row = QHBoxLayout()
        calc_row.setSpacing(6)

        for label_text, attr, default in [('a:', 'int_a', -1), ('b:', 'int_b', 1)]:
            pair = QWidget()
            pair_layout = QHBoxLayout(pair)
            pair_layout.setContentsMargins(0, 0, 0, 0)
            pair_layout.setSpacing(2)
            pair_layout.addWidget(QLabel(label_text))
            spin = self._make_spin(default, -1000, 1000, step=0.5)
            setattr(self, attr, spin)
            pair_layout.addWidget(spin)
            calc_row.addWidget(pair)

        self.int_btn = QPushButton("İntegral Al")
        self.int_btn.clicked.connect(self._on_calc_integral)
        calc_row.addWidget(self.int_btn)

        self.deriv_btn = QPushButton("Türev Al")
        self.deriv_btn.clicked.connect(self._on_calc_derivative)
        calc_row.addWidget(self.deriv_btn)

        self.calc_clear_btn = QPushButton()
        self.calc_clear_btn.setIcon(QIcon('assets/cancel.ico'))
        self.calc_clear_btn.setFixedSize(28, 28)
        self.calc_clear_btn.setToolTip('Temizle')
        self.calc_clear_btn.clicked.connect(self._on_clear_extras)
        calc_row.addWidget(self.calc_clear_btn)

        vbox.addLayout(calc_row)

        # --- Sonuçlar ---
        vbox.addWidget(QLabel('Sonuçlar:'))
        self.results = ResultsCanvas(self)
        vbox.addWidget(self.results)

        vbox.addStretch()

        scroll.setWidget(inner)

        outer = QVBoxLayout(group)
        outer.setContentsMargins(4, 8, 4, 4)
        outer.addWidget(scroll)

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
    _ROW_H   = 44   # piksel / satır (32 min + 6 spacing + 2+2 margin)
    _MAX_FN_H = 220  # scroll devreye giriyor

    def _update_fn_scroll_height(self):
        n = max(len(self._rows), 1)
        h = n * self._ROW_H + 4
        self._fn_scroll.setFixedHeight(min(h, self._MAX_FN_H))

    def _add_row(self):
        index = len(self._rows) + 1
        color = COLORS[(index - 1) % len(COLORS)]
        row = FormulaRow(color=color, index=index, parent=self)
        row.text_changed.connect(self._on_row_text_changed)
        row.remove_requested.connect(self._remove_row)
        self._rows.append(row)
        self._rows_layout.addWidget(row)
        self._update_fn_scroll_height()

    def _remove_row(self, row: FormulaRow):
        if len(self._rows) == 1:
            row.input.clear()
            return
        self._rows.remove(row)
        row.setParent(None)
        row.deleteLater()
        for i, r in enumerate(self._rows):
            r.set_index(i + 1)
        self._update_fn_scroll_height()

    def _get_parsed_rows(self) -> list:
        """Boş olmayan ve parse edilebilen satırları [(row, expr)] döndürür."""
        result = []
        for row in self._rows:
            text = row.text()
            if not text:
                continue
            try:
                result.append((row, parse_formula(text)))
            except Exception:
                pass
        return result

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
        x_min, x_max = self.min_spin.value(), self.max_spin.value()
        if x_min >= x_max:
            QMessageBox.warning(self, 'Uyarı', 'Min değeri Max değerinden küçük olmalıdır.')
            return

        functions, errors = [], []
        for row in self._rows:
            text = row.text()
            if not text:
                continue
            try:
                expr = parse_formula(text)
                functions.append((lambdify(X, expr, modules=['numpy']), latex(expr), row.color))
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
        self.results.clear_results()

    def _on_calc_derivative(self):
        parsed = self._get_parsed_rows()
        if not parsed:
            QMessageBox.warning(self, 'Uyarı', 'Geçerli fonksiyon bulunamadı.')
            return

        lines = []
        deriv_funcs = []
        for i, (row, expr) in enumerate(parsed, 1):
            try:
                deriv_expr = diff(expr, X)
                deriv_func = lambdify(X, deriv_expr, modules=['numpy'])
                deriv_funcs.append((deriv_func, latex(deriv_expr), row.color))
                lines.append((f"f{i}'(x) =", latex(deriv_expr), row.color))
            except Exception:
                lines.append((f"f{i}'(x) =", r'\text{Hata}', row.color))

        self.results.show(lines)
        self.plot_canvas.add_derivatives(deriv_funcs)

    def _on_calc_integral(self):
        a, b = self.int_a.value(), self.int_b.value()
        if a >= b:
            QMessageBox.warning(self, 'Uyarı', 'a değeri b değerinden küçük olmalıdır.')
            return

        parsed = self._get_parsed_rows()
        if not parsed:
            QMessageBox.warning(self, 'Uyarı', 'Geçerli fonksiyon bulunamadı.')
            return

        lines = []
        fill_infos = []
        for i, (row, expr) in enumerate(parsed, 1):
            func = lambdify(X, expr, modules=['numpy'])
            fill_infos.append((func, a, b, row.color))

            # Belirsiz integral (antitürev)
            try:
                antideriv = integrate(expr, X)
                lines.append((f"∫f{i} dx =", latex(antideriv) + ' + C', row.color))
            except Exception:
                lines.append((f"∫f{i} dx =", r'\text{bulunamadı}', row.color))

            # Belirli integral (sayısal değer)
            label = f"∫f{i} [{a:.2g}→{b:.2g}] ="
            try:
                result_sym = integrate(expr, (X, a, b))
                value = float(N(result_sym, 10))
                lines.append((label, f'{value:.6g}', row.color))
            except Exception:
                try:
                    xs = np.linspace(a, b, 50_000)
                    ys = np.where(np.isfinite(func(xs)), func(xs), 0.0)
                    value = float(np.trapz(ys, xs))
                    lines.append((label, f'{value:.6g}\\,(\\approx)', row.color))
                except Exception:
                    lines.append((label, r'\text{Hata}', row.color))

        self.results.show(lines)
        self.plot_canvas.add_fills(fill_infos)

    def _on_clear_extras(self):
        self.results.clear_results()
        self.plot_canvas.clear_extras()


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
