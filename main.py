import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QApplication
from app.windows.main_window import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
