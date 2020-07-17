from tkinter import *
from threading import Thread, ThreadError
from datetime import datetime

from OOP import *
import local_en as local
import regression


class InsideApp(Tk):

    def __init__(self, upper_app):
        super().__init__()
        self.title(local.NEW_TITLE)
        self.upper_app = upper_app

        Button(self, text=local.EXIT, command=self.exit_small).grid(row=0, column=0)
        Button(self, text=local.BUTTON_SELECT, command=self.get_selected).grid(row=0, column=1)
        Label(self, text=local.DEPENDENT_VARIABLE_SELECTION).grid(row=1, column=0, columnspan=2)
        self.inner_listbox = Listbox(self, selectmode=SINGLE, width=self.upper_app.LIST_WIDTH,
                                     height=self.upper_app.ELEMENTS_IN_LIST)
        self.inner_listbox.grid(row=2, column=0, columnspan=2)
        self.inner_listbox.bind('<BackSpace>', self.del_listbox_item)

        for item in self.upper_app.chosen_variables:
            self.inner_listbox.insert(END, item)

        self.bind('<Return>', self.get_selected)

    def get_selected(self, event1=None):
        """

        :param event1: Tk event
        :return: None
        """

        try:
            self.upper_app.dependent_variable = self.inner_listbox.get(self.inner_listbox.curselection()[0])
            self.exit_small()

            try:
                self.upper_app.data = self.upper_app.wb_data.get_data(self.upper_app.chosen_variables)
                dep_data = self.upper_app.data[
                    (self.upper_app.wb_data.get_id_by_name([self.upper_app.dependent_variable])[0])].fillna(
                    method='bfill')
                dep_data = dep_data.iloc[::-1]
                self.upper_app.wb_data.current_dep_data = dep_data

                if self.upper_app.model_to_use == 'ARIMA':
                    try:
                        ar_p = int(self.upper_app.p.get())
                        int_d = int(self.upper_app.d.get())
                        ma_q = int(self.upper_app.q.get())
                        frcst = int(self.upper_app.forecast.get())

                        res = regression.arima_model(self.upper_app.dependent_variable, dep_data,
                                                     ar_p, int_d, ma_q,
                                                     prdct=frcst)
                        self.upper_app.regression_results = res[0]
                        self.upper_app.to_plot_data = res[1]
                        self.upper_app.to_plot_data1 = res[2]
                        self.upper_app.message_object['text'] = local.PUSH_RESULTS + '\n' + local.PUSH_GRAPH

                        self.upper_app.chosen_variables.clear()

                    except BaseException as error:
                        self.upper_app.message_object['text'] = error

                elif self.upper_app.model_to_use == 'LINEAR':
                    indep_data = pd.DataFrame()
                    independent_chosen_variables = self.upper_app.chosen_variables.difference(
                        {self.upper_app.dependent_variable})
                    for var in independent_chosen_variables:
                        independent_data = self.upper_app.data[
                            (self.upper_app.wb_data.get_id_by_name([var])[0])].fillna(method='bfill')
                        independent_data = independent_data.iloc[::-1]
                        indep_data[var] = independent_data

                    self.upper_app.wb_data.current_indep_data = indep_data
                    res = regression.linear_model(self.upper_app.dependent_variable,
                                                  dep_data,
                                                  indep_data)
                    self.upper_app.regression_results = res[0]
                    self.upper_app.to_plot_data = res[1]
                    self.upper_app.message_object['text'] = local.PUSH_RESULTS + '\n' + local.PUSH_GRAPH

                    self.upper_app.chosen_variables.clear()

                else:
                    self.upper_app.message_object['text'] = local.NO_MODEL_CHOSEN

            except Exception as error:
                self.upper_app.message_object['text'] = local.ERROR_INDICATOR_NOT_FOUND + ':\n' + str(error)
                self.upper_app.chosen_variables.clear()

        except IndexError:
            self.upper_app.chosen_variables.clear()

    def exit_small(self, event1=None):
        """

        :param event1: Tk event
        :return: None
        """

        self.destroy()

        del self

    def del_listbox_item(self, event=None):
        """

        :param event: Tk event
        :return: None
        """

        self.inner_listbox.delete(self.inner_listbox.curselection())


class App(Tk):

    DEFAULT_FR_DATE = '1995'
    DEFAULT_TO_DATE = '2020'
    DEFAULT_KEYWORDS = local.DEFAULT_KEYWORDS
    DEFAULT_p = local.P
    DEFAULT_d = DEFAULT_p
    DEFAULT_q = DEFAULT_p
    BUTTON_WIDTH = 10
    ELEMENTS_IN_LIST = 29
    LIST_WIDTH = 29

    def __init__(self):
        super().__init__()

        self.title(local.ROOT_TITLE)
        self.geometry('927x710')
        self.resizable(width=True, height=True)

        self.top_frame = Frame(self)
        self.top_frame.grid(row=0, column=0, columnspan=8, sticky=E)
        self.left_frame = Frame(self)
        self.left_frame.grid(row=1, column=0, columnspan=3, sticky=W)
        self.right_frame = Frame(self)
        self.right_frame.grid(row=1, column=3, columnspan=6, sticky=E)
        self.bottom_frame = Frame(self, height=100)
        self.bottom_frame.grid(row=2, column=0, columnspan=8, sticky=S)
        self.chosen_variables = set()
        self.dependent_variable = ''
        self.model_to_use = ''
        self.regression_results = ''
        self.results_object = 'filename'
        self.wb_data = None
        self.data_wb = None
        self.data = None
        self.to_plot_data = None
        self.to_plot_data1 = None

        # Buttons and Radiobuttons ------------------------------------------
        self.exit_button = Button(self.top_frame,
                                  width=App.BUTTON_WIDTH, height=int(App.BUTTON_WIDTH / 2),
                                  text=local.EXIT,
                                  command=self.exit_button_bound)
        self.exit_button.grid(row=0, column=0, sticky=N + E, rowspan=3)

        self.load_button = Button(self.top_frame,
                                  width=App.BUTTON_WIDTH, height=int(App.BUTTON_WIDTH / 2),
                                  text=local.LOAD_GRAPH,
                                  command=self.save_figure_load_button_bound)
        self.load_button.grid(row=0, column=1, sticky=N + E, rowspan=3)

        self.results_button = Button(self.top_frame,
                                     width=App.BUTTON_WIDTH, height=int(App.BUTTON_WIDTH / 2),
                                     text=local.SHOW_RESULTS,
                                     command=self.results_button_bound)
        self.results_button.grid(row=0, column=4, sticky=N + W, rowspan=3)

        self.data_load_button = Button(self.top_frame,
                                       width=App.BUTTON_WIDTH, height=int(App.BUTTON_WIDTH / 2),
                                       text=local.LOAD_VARIABLES,
                                       command=self.data_load_button_bound)
        self.data_load_button.grid(row=0, column=5, sticky=N + W, rowspan=3)

        self.enter_variables_button = Button(self.top_frame,
                                             width=App.BUTTON_WIDTH, height=int(App.BUTTON_WIDTH / 2),
                                             text=local.ENTER_VARIABLES,
                                             command=self.enter_variables_button_bound)
        self.enter_variables_button.grid(row=0, column=6, sticky=N + W, rowspan=3)

        self.model_var = StringVar()
        self.ecm_model_button = Radiobutton(master=self.top_frame, indicatoron=0,
                                            text='LINEAR', variable=self.model_var,
                                            value='LINEAR', command=self.model_bound)
        self.arima_model_button = Radiobutton(master=self.top_frame, indicatoron=0,
                                              text='ARIMA', variable=self.model_var,
                                              value='ARIMA', command=self.model_bound)
        self.ecm_model_button.grid(row=1, column=7, sticky=W)
        self.arima_model_button.grid(row=2, column=7, sticky=W)

        # -------------------------------------------------------------------

        # Frames and Labels -------------------------------------------------
        Label(self.top_frame,
              text=local.FROM_DATE).grid(row=0, column=2)
        Label(self.top_frame,
              text=local.TO_DATE).grid(row=0, column=3)

        self.fr_date = Entry(self.top_frame)
        self.to_date = Entry(self.top_frame)

        self.fr_date.insert(0, App.DEFAULT_FR_DATE)
        self.to_date.insert(0, App.DEFAULT_TO_DATE)
        self.fr_date.grid(row=1, column=2)
        self.to_date.grid(row=1, column=3)

        self.p = Entry(self.bottom_frame)
        self.d = Entry(self.bottom_frame)
        self.q = Entry(self.bottom_frame)

        self.pl = Label(self.bottom_frame, text=local.AUTO_REGRESSION)
        self.dl = Label(self.bottom_frame, text=local.INTEGRATED)
        self.ql = Label(self.bottom_frame, text=local.MOV_A)

        self.p.insert(0, App.DEFAULT_p)
        self.d.insert(0, App.DEFAULT_d)
        self.q.insert(0, App.DEFAULT_q)

        self.forecast = Entry(self.bottom_frame)
        self.forecast_label = Label(self.bottom_frame, text=local.PROJECTION_PERIOD)
        self.forecast.insert(0, '1')

        self.warning_label = Label(self.bottom_frame, text=local.WARNING)

        self.keyword_text = Entry(self.top_frame, width=App.LIST_WIDTH + 10)
        self.keyword_text.insert(0, App.DEFAULT_KEYWORDS)
        self.keyword_text.grid(row=2, column=2, columnspan=2)

        Label(self.left_frame,
              text=local.ANALYZE_VARIABLES).grid(row=0, column=0, columnspan=2)

        self.listbox = Listbox(self.left_frame, height=App.ELEMENTS_IN_LIST, width=App.LIST_WIDTH,
                               selectmode=MULTIPLE)
        self.listbox.grid(row=1, column=0, columnspan=2)

        self.graph_object = PlotWindow(self.right_frame)

        self.message_object = Label(self.bottom_frame, text=(local.WELCOME + ' ' + local.PUSH_LOAD_VARIABLES))
        self.message_object.grid(row=2, column=0, columnspan=8)

        Label(self.top_frame, text=local.MODEL).grid(row=0, column=7, sticky=W)

        self.listbox.bind('<Return>', self.enter_variables_button_bound)
        self.bind('<Escape>', self.exit_button_bound)

    def save_figure_load_button_bound(self, event=None):
        """
        Bound events on Load button

        :param event: Tk event, optional
        :return: None
        """

        self.load_button.config(relief=SUNKEN)

        try:

            if self.to_plot_data:

                self.graph_object.destroy()
                self.graph_object = PlotWindow(self.right_frame)
                mpl_subplot = MPLPlot()
                mpl_subplot.build_scatter_plot(tuple(self.to_plot_data.keys()),
                                               tuple(self.to_plot_data.values()),
                                               'Y')
                self.to_plot_data.clear()

                if self.to_plot_data1:
                    mpl_subplot.build_scatter_plot(tuple(self.to_plot_data1.keys()),
                                                   tuple(self.to_plot_data1.values()),
                                                   'Predicted Y')
                    self.to_plot_data1.clear()

                now = str(datetime.now().timestamp())
                filename = 'images/' + self.model_to_use + '_' + '_'.join(self.dependent_variable.split()) + \
                           '_' + now[:now.find('.')] + '.jpg'
                mpl_subplot.suptitle(local.GRAPH_TITLE)
                mpl_subplot.nice_plot('Year', self.dependent_variable)
                mpl_subplot.savefig(filename, dpi=500)
                self.graph_object.add_mpl_figure(mpl_subplot)
                self.graph_object.grid(row=0, column=0, columnspan=5, sticky=N)

            else:
                self.message_object['text'] = local.PLOT_ALREADY

        except Exception as error:
            self.message_object['text'] = error

        self.load_button.config(relief=RAISED)

    def model_bound(self, event=None):
        """

        :param event: Tk event, optional
        :return: None
        """

        self.model_to_use = self.model_var.get()

        if self.model_to_use == 'ARIMA':

            self.warning_label.grid(row=1, column=2, columnspan=3)

            self.p.grid(row=0, column=1)
            self.d.grid(row=0, column=3)
            self.q.grid(row=0, column=5)

            self.pl.grid(row=0, column=0)
            self.dl.grid(row=0, column=2)
            self.ql.grid(row=0, column=4)

            self.forecast_label.grid(row=1, column=0)
            self.forecast.grid(row=1, column=1)

        else:
            objs = [self.p, self.d, self.q,
                    self.pl, self.dl, self.ql,
                    self.forecast, self.forecast_label,
                    self.warning_label]

            for obj in objs:
                obj.grid_forget()

    def results_button_bound(self, event=None):
        """

        :param event: Tk event, optional
        :return: None
        """

        self.results_button.config(relief=SUNKEN)

        try:
            new_window = Tk()
            new_window.title(self.regression_results)

            with open(self.regression_results) as a:
                lbl = Label(new_window, text=a.read())
            lbl.pack()

            new_window.mainloop()

        except FileNotFoundError:
            self.message_object['text'] = self.regression_results

        except Exception as error:
            self.message_object['text'] = error

        self.results_button.config(relief=RAISED)

    def go(self):

        self.listbox.delete(0, END)
        try:

            self.wb_data = DataSet(start_year=self.fr_date.get(), stop_year=str(int(self.to_date.get()) + 1))
            self.data_wb = self.wb_data.get_data_id(self.keyword_text.get())

            class_error = self.wb_data.current_error
            if class_error:
                self.message_object['text'] = class_error

            for data_item in self.data_wb:
                self.listbox.insert(END, data_item)

            self.message_object['text'] = local.CHOOSE_MODEL

        except ValueError:
            self.message_object['text'] = local.ERROR_WRONG_YEAR

    def data_load_button_bound(self, event=None):
        """
        Bound events on Load Data button

        :param event: Tk event, optional
        :return: None
        """

        self.data_load_button.config(relief=SUNKEN)
        self.message_object['text'] = local.WELCOME

        try:

            self.message_object['text'] = local.LOADING

            t1 = Thread(target=self.go)
            t1.setDaemon(True)
            t1.start()

        except BaseException as error:
            self.message_object['text'] = error

        except ThreadError as te:
            self.message_object['text'] = te

        self.data_load_button.config(relief=RAISED)

    def enter_variables_button_bound(self, event=None):
        """

        :param event: Tk event, optional
        :return: None
        """

        self.enter_variables_button.config(relief=SUNKEN)

        for item in self.listbox.curselection():
            self.chosen_variables.add(self.listbox.get(item))

        master = InsideApp(self)
        master.mainloop()

        self.enter_variables_button.config(relief=RAISED)

    def exit_button_bound(self, event=None):
        """
        Bound events on Exit button

        :param event: Tk event, optional
        :return: None
        """

        self.exit_button.config(relief=SUNKEN)
        self.destroy()
        del self

        try:
            exit()

        except KeyboardInterrupt:
            pass


new_app = App()
new_app.mainloop()
