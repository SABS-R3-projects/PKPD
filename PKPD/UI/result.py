"""Script to display output after modelling and inference. Refactoring of this code is very likely.

##################    What it should do:    ######################
    - get the data as numpy array
    - get ODE solution as numpy array
    - get infered parameters as numpy array

    - display infered parameters in a table:
        parameter 1 [unit] | parameter 2 [unit] | ...
        value              | value              | ...

    - display data as scatter plot
    - display solution as line plot
"""

from PyQt5 import uic
from PyQt5.QtWidgets import (QMainWindow, QWidget, QApplication, QGridLayout, QLabel,
QTextEdit, QLineEdit)
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        title = QLabel('Title')
        author = QLabel('Author')
        review = QLabel('Review')

        titleEdit = QLineEdit()
        authorEdit = QLineEdit()
        reviewEdit = QTextEdit()

        self.graphWidget = pg.PlotWidget()

        ### Layout
        #self.setCentralWidget(self.graphWidget)
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(review, 3, 0)
        grid.addWidget(reviewEdit, 3, 1)

        grid.addWidget(self.graphWidget, 4, 1)

        self.setLayout(grid)

        hour = [1,2,3,4,5,6,7,8,9,10]
        temperature = [30,32,34,32,33,31,29,32,35,45]

        self.graphWidget.setBackground('w')
        self.graphWidget.addLegend()

        # plot data: x, y values
        ## plot solid line
        pen = pg.mkPen(color='k', width=5, style=pg.QtCore.Qt.DashLine)
        self.graphWidget.plot(hour, temperature, pen=pen, name='line')
        ## scatter plot
        self.graphWidget.plot(hour, temperature, symbol='o', symbolSize=7, symbolBrush=pg.mkBrush(255, 0, 0, 120), symbolPen='k',
                              pen=pg.mkPen(None), name='data')

        self.graphWidget.setTitle("Your Title Here")
        self.graphWidget.setLabel('left', 'Temperature (°C)', color='gray', size=10)
        self.graphWidget.setLabel('bottom', 'Hour (H)', color='gray', size=10)


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()