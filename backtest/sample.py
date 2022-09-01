from localbacktest import *
LbtConfig.set_datasource('local')

from IPython.display import display
from datetime import datetime
import pandas as pd

def initialize(context):
    context.securities = ['600030.SH']
    context.start_date = '2021-03-01'
    context.end_date = '2022-01-01'
    context.capital = 500000
    context.benchmark = '000300.SH'
    context.commission = 0.0003

def handle_data(datetime, context, data):
    lbt.order('600030.SH', 100, 'buy', 'open')

lbt = LocalBacktest(init_func=initialize, handle_data_func=handle_data)
lbt.run()
display(lbt.summary_result())
lbt.plot()

