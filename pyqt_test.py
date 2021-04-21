import sys
import matplotlib
# matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from housing_visualization.gui.Map import Map


# class MplCanvas(FigureCanvasQTAgg):
#
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         self.fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = self.fig.add_subplot(111)
#         super(MplCanvas, self).__init__(self.fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        sys._excepthook = sys.excepthook

        def exception_hook(exctype, value, traceback):
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback)
            sys.exit(1)

        sys.excepthook = exception_hook

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        map = Map(self, width=16, height=8, dpi=100)
        self.setCentralWidget(map)

        self.show()


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()