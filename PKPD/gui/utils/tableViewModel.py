import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtGui


class PandasModel(QtCore.QAbstractTableModel):
    """PandasModel class extending QAbstractTableModel for Pandas dataframes, such that PandasModel instances are compatible
    with PyQt's QTableView. In particular designed to deal with PKPD data.
    """
    def __init__(self, data:pd.DataFrame, is_id_present:bool, is_dosing_present:bool):
        QtCore.QAbstractTableModel.__init__(self)
        # replace NaN values in data by '.' to make it more familiar to users
        self._data = data.replace(np.nan, '.')

        self._is_id_present = is_id_present
        self._is_dosing_present = is_dosing_present

    def rowCount(self, parent=None):
        """Returns number of rows in dataframe.

        Returns:
            {int} -- Number of rows in dataframe.
        """
        return self._data.shape[0]

    def columnCount(self, parent=None):
        """Returns number of columns in dataframe.

        Returns:
            {int} -- Number of columns in dataframe.
        """
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole) -> None:
        """Qt internal method to display entries in QTableView. Customised to color columns by meaning (patient IDs, time, states
        dose schedule).
        """
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                # return entry in dataframe
                return str(self._data.iloc[index.row(), index.column()])

            if self._is_id_present:
                # color id column blue grey
                if role == QtCore.Qt.BackgroundRole and index.column() == 0:
                    return QtGui.QBrush(QtGui.QColor(60, 60.4, 89.8))

                # color time column (darker) grey
                if role == QtCore.Qt.BackgroundRole and index.column() == 1:
                    return QtGui.QBrush(QtGui.QColor(69.8, 69.8, 69.8))
            else:
                # color time column (darker) grey
                if role == QtCore.Qt.BackgroundRole and index.column() == 0:
                    return QtGui.QBrush(QtGui.QColor(69.8, 69.8, 69.8))

            if self._is_dosing_present:
                last_column_id = self.columnCount()-1
                # color last column red grey
                if role == QtCore.Qt.BackgroundRole and index.column() == last_column_id:
                    return QtGui.QBrush(QtGui.QColor(89.8, 60, 61.2))

        return None

    def headerData(self, col, orientation, role):
        """Qt internal method to display headers in QTableView.
        """
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None