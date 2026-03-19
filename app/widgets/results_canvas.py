from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy


class ResultsCanvas(FigureCanvas):
    LINE_H = 42  # piksel / satır

    def __init__(self, parent=None):
        self.fig = Figure(facecolor='#f5f5f5')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(0)

    def show(self, lines: list):
        """lines: [(label_str, latex_body, color), ...]
           latex_body → LaTeX string veya None
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
