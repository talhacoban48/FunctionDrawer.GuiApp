import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(facecolor='white')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax = self.fig.add_subplot(111)
        self._base:   list = []   # (func, latex_str, color)
        self._derivs: list = []   # (func, latex_str, color)
        self._fills:  list = []   # (func, a, b, color)
        self._x_range = (-10.0, 10.0, 0.01)
        self._draw_empty()

    # --- iç yardımcılar ---
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
            fill_x2, fill_y = self._safe_eval(func, fill_x)
            self.ax.fill_between(fill_x2, fill_y, 0,
                                 alpha=0.25, color=color,
                                 label=f'Alan $[{a:.3g},\\ {b:.3g}]$')

        self._style_axes()
        if self._base or self._derivs or self._fills:
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
        self._derivs = deriv_funcs
        self._redraw()

    def add_fills(self, fill_infos: list):
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
