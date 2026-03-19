import numpy as np
from sympy import latex, lambdify, diff, integrate, N

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QLabel, QPushButton, QDoubleSpinBox, QFormLayout,
    QSizePolicy, QMessageBox, QScrollArea, QFrame,
)
from PyQt5.QtGui import QFont, QIcon

from app.constants import asset, parse_formula, COLORS, X
from app.widgets.formula_row    import FormulaRow
from app.widgets.preview_canvas  import PreviewCanvas
from app.widgets.results_canvas  import ResultsCanvas
from app.widgets.plot_canvas     import PlotCanvas


class MainWindow(QMainWindow):
    _ROW_H    = 44
    _MAX_FN_H = 220

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Function Drawer')
        self.setWindowIcon(QIcon(asset('favicon.ico')))
        self.setMinimumSize(960, 640)
        self._rows: list[FormulaRow] = []
        self._build_ui()
        self._add_row()

    # ── UI inşası ────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(self._left_panel())
        layout.addWidget(self._right_panel(), stretch=1)

    def _left_panel(self) -> QGroupBox:
        group = QGroupBox('Fonksiyonlar')
        group.setFixedWidth(420)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        vbox = QVBoxLayout(inner)
        vbox.setSpacing(10)
        vbox.setContentsMargins(4, 4, 4, 4)

        # Fonksiyon listesi
        self._fn_scroll = QScrollArea()
        self._fn_scroll.setWidgetResizable(True)
        self._fn_scroll.setFrameShape(QFrame.NoFrame)
        self._fn_scroll.setHorizontalScrollBarPolicy(0x1)
        self._rows_widget = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setSpacing(6)
        self._rows_layout.setContentsMargins(0, 2, 0, 2)
        self._fn_scroll.setWidget(self._rows_widget)
        vbox.addWidget(self._fn_scroll)

        add_btn = QPushButton(' Fonksiyon Ekle')
        add_btn.setIcon(QIcon(asset('add.ico')))
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
        self.min_spin  = self._make_spin(-10,   -1000, 1000, step=1.0)
        self.max_spin  = self._make_spin( 10,   -1000, 1000, step=1.0)
        self.step_spin = self._make_spin(0.01, 0.0001, 10.0, step=0.01, decimals=4)
        form.addRow('Min:',  self.min_spin)
        form.addRow('Max:',  self.max_spin)
        form.addRow('Adım:', self.step_spin)
        vbox.addWidget(form_widget)

        # Çiz / Temizle
        btn_row = QHBoxLayout()
        self.draw_btn = QPushButton(' Çiz')
        self.draw_btn.setIcon(QIcon(asset('search.ico')))
        self.draw_btn.setMinimumHeight(36)
        self.draw_btn.setDefault(True)
        self.clear_btn = QPushButton(' Temizle')
        self.clear_btn.setIcon(QIcon(asset('cancel.ico')))
        self.clear_btn.setMinimumHeight(36)
        self.draw_btn.clicked.connect(self._on_draw)
        self.clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(self.draw_btn)
        btn_row.addWidget(self.clear_btn)
        vbox.addLayout(btn_row)

        # Ayraç
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        vbox.addWidget(sep)

        # Hesaplamalar
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

        self.int_btn = QPushButton('İntegral Al')
        self.int_btn.clicked.connect(self._on_calc_integral)
        calc_row.addWidget(self.int_btn)

        self.deriv_btn = QPushButton('Türev Al')
        self.deriv_btn.clicked.connect(self._on_calc_derivative)
        calc_row.addWidget(self.deriv_btn)

        self.calc_clear_btn = QPushButton()
        self.calc_clear_btn.setIcon(QIcon(asset('cancel.ico')))
        self.calc_clear_btn.setFixedSize(28, 28)
        self.calc_clear_btn.setToolTip('Temizle')
        self.calc_clear_btn.clicked.connect(self._on_clear_extras)
        calc_row.addWidget(self.calc_clear_btn)

        vbox.addLayout(calc_row)

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

    # ── Satır yönetimi ───────────────────────────────────────────────────────

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

    # ── Slot'lar ─────────────────────────────────────────────────────────────

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

        lines, deriv_funcs = [], []
        for i, (row, expr) in enumerate(parsed, 1):
            try:
                deriv_expr = diff(expr, X)
                deriv_funcs.append((lambdify(X, deriv_expr, modules=['numpy']), latex(deriv_expr), row.color))
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

        lines, fill_infos = [], []
        for i, (row, expr) in enumerate(parsed, 1):
            func = lambdify(X, expr, modules=['numpy'])
            fill_infos.append((func, a, b, row.color))

            try:
                antideriv = integrate(expr, X)
                lines.append((f'∫f{i} dx =', latex(antideriv) + ' + C', row.color))
            except Exception:
                lines.append((f'∫f{i} dx =', r'\text{bulunamadı}', row.color))

            label = f'∫f{i} [{a:.2g}→{b:.2g}] ='
            try:
                value = float(N(integrate(expr, (X, a, b)), 10))
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
