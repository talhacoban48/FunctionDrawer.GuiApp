from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy


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
