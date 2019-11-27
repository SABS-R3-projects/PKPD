from abc import ABC, abstractmethod

class AbstractData(ABC):
    def __init__(self):
        self.datafile = None

    def read_file(self):
        # read data from a csv (or other) file
        raise NotImplementedError

    def set_datafile(self):
        # set self.datafile using read_file
        raise NotImplementedError
