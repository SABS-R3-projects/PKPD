from abc import ABC, abstractmethod

class AbstractMainWindow(ABC):
    def __init__(self):
        # initialise window size, style, icon, windowname, tab structure
        raise NotImplementedError

    @abstractmethod
    def _set_window_size(self):
        # set the default window size (make sure not fixed)
        raise NotImplementedError

    @abstractmethod
    def _set_geometry(self):
        # set the window layout
        raise NotImplementedError

    @abstractmethod
    def _set_style(self):
        # set style
        raise NotImplementedError

    @abstractmethod
    def _set_icon(self):
        # st application icon
        raise NotImplementedError

    @abstractmethod
    def _set_windowname(self):
        # set window name for top
        raise NotImplementedError

    @abstractmethod
    def _set_tab_structure(self):
        # set the structure of tabs within the window
        raise NotImplementedError

    @abstractmethod
    def _change_tab(self):
        # redraw to a different tab type
        raise NotImplementedError

    @abstractmethod
    def _exit(self):
        # exit the application gracefully
        raise NotImplementedError

class AbstractTab(ABC):
    @abstractmethod
    def _make_button(self):
        # draw a button
        raise NotImplementedError

    @abstractmethod
    def _make_multiline_textbox(self):
        # draw a textbox for text input
        raise NotImplementedError

    @abstractmethod
    def _make_graph(self):
        # instantiate a graph object
        raise NotImplementedError

    @abstractmethod
    def _make_table(self):
        # make a tabular object
        raise NotImplementedError

