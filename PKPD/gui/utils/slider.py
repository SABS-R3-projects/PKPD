from PyQt5 import QtWidgets, QtCore


class DoubleSlider(QtWidgets.QSlider):
    """Extension to QSlider class that allows for float precision in slider values. Qts QSlider can only in/decrement their values
    in integer steps, which is modified by this class

    Arguments:
        {QSlider} -- PyQt5's slider class.
    """
    # create our our signal that we can connect to if necessary
    doubleValueChanged = QtCore.pyqtSignal(float)

    def __init__(self, decimals=1):
        super(DoubleSlider, self).__init__(QtCore.Qt.Horizontal)

        # compute magnitude difference between integer QSlider and DoubleSlider
        self._unit_conversion_factor = 10 ** decimals

        # spread tick intervals according to chosen units (avoid having too narrow ticks)
        self.setTickInterval()

        # connect slider changes to a method that can deal with the wanted decimal precision
        self.valueChanged.connect(self.emitDoubleValueChanged)


    def emitDoubleValueChanged(self):
        """Reaction to changing the slider position. Emits the slider value in the appropriate precision.
        """
        # get QSlider value
        qslider_value = float(super(DoubleSlider, self).value())

        # scale to appropriate units
        value = qslider_value / self._unit_conversion_factor

        # emit value
        self.doubleValueChanged.emit(value)


    def value(self):
        """Returns the current value of the slider in the appropriate precision.

        Returns:
            {float} -- Returns slider value.
        """
        # get QSlider value
        qslider_value = super(DoubleSlider, self).value()

        # scale to appropriate units
        value = float(qslider_value) / self._unit_conversion_factor

        return value


    def setMinimum(self, minimum):
        """Sets minimum of slider range.

        Arguments:
            minimum {float} --  Minimum of slider range.
        """
        # rescale to appropriate units
        qslider_minimum = int(minimum * self._unit_conversion_factor)

        # set QSlider minimum
        super(DoubleSlider, self).setMinimum(qslider_minimum)


    def setMaximum(self, maximum):
        """Sets maximum of slider range.

        Arguments:
            maximum {float} --  Maximum of slider range.
        """
        # rescale to appropriate units
        qslider_maximum = int(maximum * self._unit_conversion_factor)

        # set QSlider maximum
        super(DoubleSlider, self).setMaximum(qslider_maximum)


    def setValue(self, value):
        """Sets position of slider to given value.

        Arguments:
            value {float} -- Value the slider will be set to.
        """
        # rescale to appropriate units
        qslider_value = int(value * self._unit_conversion_factor)

        # set QSlider value
        super(DoubleSlider, self).setValue(qslider_value)


    def setTickInterval(self):
        """Sets tick intervals to chosen level of precision.
        """
        super(DoubleSlider, self).setTickInterval(self._unit_conversion_factor)


    def minimum(self):
        """Gets minimum of slider range.

        Returns:
            minimum {float} -- Returns minimum of slider range.
        """
        # get minimum from QSlider (restricted to integers)
        qslider_minimum = super(DoubleSlider, self).minimum()

        # scale to appropriate units
        minimum = float(qslider_minimum) / self._unit_conversion_factor

        return minimum


    def maximum(self):
        """Gets maximum of slider range.

        Returns:
            maximum {float} -- Returns maximum of slider range.
        """
        # get maximum from QSlider (restricted to integers)
        qslider_maximum = super(DoubleSlider, self).maximum()

        # scale to appropriate units
        maximum = float(qslider_maximum) / self._unit_conversion_factor

        return maximum