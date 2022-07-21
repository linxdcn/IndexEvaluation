from tkinter.messagebox import NO
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker 
from enum import Enum
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from sympy import per

from evaluation.db import *
from evaluation.constant import *
import warnings

warnings.filterwarnings("ignore")

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

__all__ = [
    'line_name', 
    'plot', 
    'plot_list',
    'plot_long_pe_percent', 
    'plot_short_pe_percent',
    'plot_long_pb_percent',
    'plot_short_pb_percent',
    ]

class line_name(Enum):
    close = 'close'
    pe  = 'pe'

    close_5day_mean = 'close_5day_mean'
    close_10day_mean = 'close_10day_mean'
    close_20day_mean = 'close_20day_mean'
    close_1year_mean = 'close_1year_mean'

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

# 左y轴为close
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

    colors = [
        'xkcd:light blue',
        'xkcd:pink',
        'xkcd:turquoise',
        'xkcd:lavender',
        'xkcd:peach'
            ]

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

def plot_list(indexs, line,
        y_min = None, y_max = None, 
        y_interval = None):
    fig=plt.figure(figsize=(20,8), dpi=300)
    fig.set_facecolor('white')

    #绘制第一个Y轴
    ax=fig.add_subplot(111)
    ax.set_title(line.value, size=12)
    ax.set_xlabel("date", size=12)
    ax.set_ylabel(line.value, size=12)
    ax.grid(axis='x')
    ax.grid()

    if y_interval is not None:
        ax.yaxis.set_major_locator(ticker.MultipleLocator(y_interval))

    if y_max is not None and y_min is not None:
        ax.set_ylim([y_min, y_max])

    lines = None
    for i in range(len(indexs)):
        df_local = load_local_db_by_filename(indexs[i], period='month')
        l = ax.plot(df_local.index, df_local[line.value], color='C' + str(i % 10), label=line.value)
        if lines is None:
            lines = l
        else:
            lines = lines + l

    #合并图例
    ax.legend(lines, indexs, loc="upper left", fontsize=12)

    plt.show()

# 左y轴：close
# 右y轴：各年份pe百分比
# x轴：2000-至今
def plot_long_pe_percent(index_name):
    df_local = load_local_db(index_name, period='month')

    plot(df_local, 
            [line_name.pe_3year_percent, line_name.pe_5year_percent, line_name.pe_10year_percent, line_name.pe_history_percent],
            start_date=datetime.date(2000, 1, 1), end_date=datetime.datetime.now().date(), 
            right_y_min=0.0, right_y_max=1.0, right_y_interval=0.05)

# 左y轴：close
# 右y轴：各年份pe百分比
# x轴：近一年
def plot_short_pe_percent(index_name):
    df_local = load_local_db(index_name, period='month')

    plot(df_local, 
        [line_name.pe_3year_percent, line_name.pe_5year_percent, line_name.pe_10year_percent, line_name.pe_history_percent],
        start_date=datetime.datetime.now()-relativedelta(years=1), end_date=datetime.datetime.now().date(), 
        right_y_min=0.0, right_y_max=1.0, right_y_interval=0.05)

# 左y轴：close
# 右y轴：各年份pb百分比
# x轴：2000-至今
def plot_long_pb_percent(index_name):
    df_local = load_local_db(index_name, period='month')

    plot(df_local, 
            [line_name.pb_3year_percent, line_name.pb_5year_percent, line_name.pb_10year_percent, line_name.pb_history_percent],
            start_date=datetime.date(2010, 1, 1), end_date=datetime.datetime.now().date(), 
            right_y_min=0.0, right_y_max=1.0, right_y_interval=0.05)

# 左y轴：close
# 右y轴：各年份pb百分比
# x轴：近一年
def plot_short_pb_percent(index_name):
    df_local = load_local_db(index_name, period='month')
    plot(df_local, 
        [line_name.pb_3year_percent, line_name.pb_5year_percent, line_name.pb_10year_percent, line_name.pb_history_percent],
        start_date=datetime.datetime.now()-relativedelta(years=1), end_date=datetime.datetime.now().date(), 
        right_y_min=0.0, right_y_max=1.0, right_y_interval=0.05)