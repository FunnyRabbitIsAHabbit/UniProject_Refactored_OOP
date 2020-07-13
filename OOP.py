"""

Uni project. OOP part.

Developer: Stanislav Alexandrovich Ermokhin

"""

import tkinter as tk
from tkinter import Frame, TOP, BOTH
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,\
    NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas_datareader._utils as pdu
from pandas_datareader import wb
import pandas as pd
import seaborn as sns

import local_en as local

sns.set()


class DataSet:

    def __init__(self, countries=None,
                 indicators=None, start_year=None, stop_year=None):
        """

        :param countries: lst, optional
        :param indicators: lst, optional
        :param start_year: int, optional
        :param stop_year: int, optional
        """

        properties = self.set_default()
        self.countries = countries or properties['countries']
        self.indicators = indicators or properties['indicators']
        self.start_year = start_year if start_year and start_year < stop_year else 1995
        self.stop_year = stop_year or 2019
        self.data = None
        self.current_error = None
        self.current_dep_data = None
        self.current_indep_data = None
        self.indicators_ids_data = None

    def set_default(self, countries_filename='countries.txt',
                    indicators_filename='indicators.txt'):
        """

        :param countries_filename: str
        :param indicators_filename: str
        :return: dict
        """

        try:
            with open(countries_filename) as a:
                countries_lst = a.readlines()

            with open(indicators_filename) as a:
                indicators_lst = a.readlines()

            for i in range(len(countries_lst)):
                countries_lst[i] = countries_lst[i].rstrip()
            for j in range(len(indicators_lst)):
                indicators_lst[j] = indicators_lst[j].rstrip()

            return {'countries': countries_lst,
                    'indicators': indicators_lst}

        except FileNotFoundError:
            self.current_error = local.ERROR

            return {'countries': None,
                    'indicators': None}

    def __repr__(self):
        """

        :return: str
        """

        dic = self.__dict__

        return 'WorldBankDataSet object:\n' + \
               '\n'.join([str(key) + ': ' + str(dic[key])
                          for key in dic])

    def get_data_id(self, search_keywords):
        """

        :param search_keywords: list
        :return: list
        """

        search_keywords = search_keywords.split()
        try:
            data = wb.search('|'.join(search_keywords))
            self.data = data

            return data['name'].to_list()

        except Exception as error:
            self.current_error = error
            self.data = pd.DataFrame()

            return pd.DataFrame()

    def get_data(self, indicator_set):
        """

        :param indicator_set: set
        :return: pandas.DataFrame
        """

        try:
            data = self.data
            indicator_set_clean = data.loc[data['name'].isin(indicator_set)]['id'].to_list()
            indicators_ids_data = wb.download(country=self.countries,
                                              indicator=indicator_set_clean,
                                              start=self.start_year, end=self.stop_year)

            self.indicators_ids_data = indicators_ids_data

            return indicators_ids_data

        except AttributeError as error1:
            DataSet.current_error = local.ERROR + str(error1)

        except pdu.RemoteDataError as error2:
            DataSet.current_error = local.ERROR + str(error2)

        except Exception as error3:
            DataSet.current_error = local.ERROR + str(error3)

    def get_id_by_name(self, names):
        """

        :param names: list
        :return:
        """
        try:
            data = self.data
            indicator_set_clean = data.loc[data['name'].isin(names)]['id'].to_list()
            _ids = indicator_set_clean

            return _ids

        except AttributeError as error1:
            self.current_error = local.ERROR + str(error1)


class PlotWindow(Frame):
    """
    A MatPlotLib window
    """

    def __init__(self, window):
        """
        Class constructor

        :param window: mpl window
        """

        Frame.__init__(self, window)
        self.grid(row=3, columnspan=5)

    def unpack(self):
        """
        Delete window with MPL Figure from Tk window
        """

        self.destroy()

    def add_mpl_figure(self, figure):
        """
        Add MatPlotLib Figure

        :param figure: mpl figure
        :return: None
        """

        self.mpl_canvas = FigureCanvasTkAgg(figure, self)
        self.mpl_canvas.draw()

        self.toolbar = NavigationToolbar2Tk(self.mpl_canvas, self)
        self.toolbar.update()

        self.mpl_canvas.get_tk_widget().pack(side=TOP,
                                             fill=BOTH, expand=True)
        self.mpl_canvas._tkcanvas.pack(side=TOP,
                                       fill=BOTH, expand=True)


class MPLPlot(Figure):
    """
    A MatPlotLib figure
    """

    def __init__(self):
        """
        Class constructor
        """

        Figure.__init__(self, dpi=100)
        self.plot = self.add_subplot(111)

    def build_plot(self, plot_x, plot_y, label):
        """
        Add plot on a subplot

        :param plot_x: tuple of x_data
        :param plot_y: tuple of y_data
        :param label: label
        :return:
        """

        self.plot.plot(plot_x, plot_y, label=label)

    def build_scatter_plot(self, plot_x, plot_y, label):
        """
        Add scatter plot on a subplot

        :param plot_x: tuple of x_data
        :param plot_y: tuple of y_data
        :param label: label
        :return:
        """

        self.plot.scatter(plot_x, plot_y, label=label)

    def nice_plot(self, x_label=None, y_label=None):
        """
        Make plot look nice

        :param x_label: str
        :param y_label: str
        :return: None
        """

        self.plot.grid(True)
        if x_label and y_label:
            self.plot.set_xlabel(x_label)
            self.plot.set_ylabel(y_label)
        self.plot.legend()


class VerticalScrolledFrame:
    """
        A vertically scrolled Frame that can be treated like any other Frame
        ie it needs a master and layout and it can be a master.
        :width:, :height:, :bg: are passed to the underlying Canvas
        :bg: and all other keyword arguments are passed to the inner Frame
        note that a widget layed out in this frame will have a self.master 3 layers deep,
        (outer Frame, Canvas, inner Frame) so
        if you subclass this there is no built in way for the children to access it.
        You need to provide the controller separately.
        
        from: https://gist.github.com/novel-yet-trivial/3eddfce704db3082e38c84664fc1fdf8
        
        """

    def __init__(self, master, **kwargs):
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)
        bg = kwargs.pop('bg', kwargs.pop('background', None))
        self.outer = tk.Frame(master, **kwargs)
        self.vsb = tk.Scrollbar(self.outer, orient=tk.VERTICAL)
        self.vsb.pack(fill=tk.Y, side=tk.RIGHT)
        self.canvas = tk.Canvas(self.outer, highlightthickness=0, width=width, height=height, bg=bg)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas['yscrollcommand'] = self.vsb.set
        # mouse scroll does not seem to work with just "bind"; You have
        # to use "bind_all". Therefore to use multiple windows you have
        # to bind_all in the current widget
        self.canvas.bind_all("<Enter>", self._bind_mouse)
        self.canvas.bind_all("<Leave>", self._unbind_mouse)
        self.vsb['command'] = self.canvas.yview
        self.inner = tk.Frame(self.canvas, bg=bg)
        # pack the inner Frame into the Canvas with the topleft corner 4 pixels offset
        self.canvas.create_window(0, 0, window=self.inner, anchor='nw')
        self.inner.bind_all("<Configure>", self._on_frame_configure)
        self.outer_attr = set(dir(tk.Widget))

    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self.outer, item)
        else:
            # all other attributes (_w, children, etc) are passed to self.inner
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        self.canvas.config(scrollregion=(0, 0, x2, max(y2, height)))

    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Linux uses event.num; Windows / Mac uses event.delta"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
