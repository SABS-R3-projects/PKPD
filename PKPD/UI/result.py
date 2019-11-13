"""Script to display output after modelling and inference. Refactoring of this code is very likely.
"""

from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        hour = [1,2,3,4,5,6,7,8,9,10]
        temperature = [30,32,34,32,33,31,29,32,35,45]

        self.graphWidget.setBackground('w')
        self.graphWidget.addLegend()

        # plot data: x, y values
        ## plot solid line
        pen = pg.mkPen(color='k', width=5, style=pg.QtCore.Qt.DashLine)
        self.graphWidget.plot(hour, temperature, pen=pen, name='line')
        ## scatter plot
        self.graphWidget.plot(hour, temperature, symbol='o', symbolSize=5, symbolBrush=('r'), name='data')

        self.graphWidget.setTitle("Your Title Here")
        self.graphWidget.setLabel('left', 'Temperature (°C)', color='gray', size=10)
        self.graphWidget.setLabel('bottom', 'Hour (H)', color='gray', size=10)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()