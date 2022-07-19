import matplotlib.pyplot as plt
import matplotlib.ticker as ticker 
from enum import Enum
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

from evaluation.db import load_local_db
import warnings

warnings.filterwarnings("ignore")

__all__ = ['line_name', 'plot', 'plot_pe_percent', 'plot_pb_percent']

class line_name(Enum):
    pe  = 'pe'

    pe_5day_mean = 'pe_5day_mean'
    pe_10day_mean = 'pe_10day_mean'
    pe_20day_mean = 'pe_20day_mean'

    pe_1year_mean = 'pe_1year_mean'
    pe_3year_mean = 'pe_3year_mean'
    pe_5year_mean = 'pe_5year_mean'
    pe_10year_mean = 'pe_10year_mean'

    pe_1year_percent = 'pe_1year_percent'
    pe_3year_percent = 'pe_3year_percent'    
    pe_5year_percent = 'pe_5year_percent'
    pe_10year_percent = 'pe_10year_percent'
    pe_history_percent = 'pe_history_percent'

    pb_1year_percent = 'pb_1year_percent'
    pb_3year_percent = 'pb_3year_percent'    
    pb_5year_percent = 'pb_5year_percent'
    pb_10year_percent = 'pb_10year_percent'
    pb_history_percent = 'pb_history_percent'

def plot(df_local, line_list,
                    start_date = None, end_date = None, 
                    left_y_min = None, left_y_max = None, 
                    right_y_min = None, right_y_max = None,
                    right_y_interval = None):
    fig=plt.figure(figsize=(20,8), dpi=300)
    fig.set_facecolor('white')

    #绘制第一个Y轴
    ax=fig.add_subplot(111)
    lin0=ax.plot(df_local.index, df_local['close'], color="r", label="close")
    ax.set_title("Evaluation", size=12)
    ax.set_xlabel("date", size=12)
    ax.set_ylabel("close", size=12)
    ax.grid(axis='x')
    if start_date is not None and end_date is not None:
        ax.set_xlim([start_date, end_date])
    if left_y_max is not None and left_y_min is not None:
        ax.set_ylim([left_y_min, left_y_max])

    colors = ['xkcd:light blue',
                'xkcd:pink',
                'xkcd:turquoise',
                'xkcd:lavender',
                'xkcd:peach']
    #绘制另一Y轴    
    ax1=ax.twinx()
    for i in range(len(line_list)):
        linx = ax1.plot(df_local[line_list[i].value], color=colors[i % len(colors)], label=line_list[i].value)
        lin0=lin0+linx

    ax1.grid()
    if right_y_interval is not None:
        ax1.yaxis.set_major_locator(ticker.MultipleLocator(right_y_interval))
    ax1.set_ylabel("value", size=12)
    if right_y_max is not None and right_y_min is not None:
        ax1.set_ylim([right_y_min, right_y_max])

    #合并图例
    labs=[l.get_label() for l in lin0]
    ax.legend(lin0, labs, loc="upper left", fontsize=12)

    plt.show()

def plot_pe_percent(index_name):
    df_local = load_local_db(index_name)

    plot(df_local, 
            [line_name.pe_3year_percent, line_name.pe_5year_percent, line_name.pe_10year_percent],
            start_date=datetime.date(2010, 1, 1), end_date=datetime.datetime.now().date(), 
            right_y_min=0.0, right_y_max=1.0, right_y_interval=0.05)

    plot(df_local, 
        [line_name.pe_3year_percent, line_name.pe_5year_percent, line_name.pe_10year_percent],
        start_date=datetime.datetime.now()-relativedelta(years=1), end_date=datetime.datetime.now().date(), 
        right_y_min=0.0, right_y_max=1.0, right_y_interval=0.05)

def plot_pb_percent(index_name):
    df_local = load_local_db(index_name)

    plot(df_local, 
            [line_name.pb_3year_percent, line_name.pb_5year_percent, line_name.pb_10year_percent],
            start_date=datetime.date(2010, 1, 1), end_date=datetime.datetime.now().date(), 
            right_y_min=0.0, right_y_max=1.0, right_y_interval=0.05)

    plot(df_local, 
        [line_name.pb_3year_percent, line_name.pb_5year_percent, line_name.pb_10year_percent],
        start_date=datetime.datetime.now()-relativedelta(years=1), end_date=datetime.datetime.now().date(), 
        right_y_min=0.0, right_y_max=1.0, right_y_interval=0.05)