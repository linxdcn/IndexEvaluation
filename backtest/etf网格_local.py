from json import load
from localbacktest import *
LbtConfig.set_datasource('local')

from IPython.display import display
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import os
import math

def initialize(context):
    context.securities = ['510300.SH']
    context.start_date = '2016-01-01'
    context.end_date = '2022-07-01'
    context.capital = 1200000
    context.benchmark = '000300.SH'
    context.commission = 0.0003

    context.index = '沪深300'

    startd = datetime.datetime.strptime(context.start_date, "%Y-%m-%d").date()
    oneday_befor_startd = startd-relativedelta(days=1)

    df = load_local_pe(context.index, oneday_befor_startd-relativedelta(years=10), oneday_befor_startd)
    context.pe_10year = df['pe']

    df = get_market_data([context.securities[0]], (startd-relativedelta(years=1)).strftime("%Y-%m-%d"), context.start_date)
    context.close_1year = df.loc[context.securities[0], 'close']

    start_d = datetime.datetime.strptime(context.start_date, "%Y-%m-%d").date()
    end_d = datetime.datetime.strptime(context.end_date, "%Y-%m-%d").date()
    df = load_local_pe(context.index, start_d, end_d)
    context.pe_all = df

    df = get_market_data([context.securities[0]], context.start_date, context.end_date)
    context.security_all = df

    context.start = False
    context.init_price = 0
    context.interval = 0

    context.value_size = context.capital / 12

    context.min_net = []
    context.mid_net = []
    context.max_net = []

def handle_data(bar_datetime, context, bar_data):

    pe_ttm = context.pe_all.loc[bar_datetime.date(), 'pe']
    close = context.security_all.loc[context.securities[0]].loc[bar_datetime.date(), 'close']

    if not context.start:
        if pe_ttm < context.pe_10year.dropna().mean():
            context.start = True
            context.init_price = close
            context.interval = context.close_1year.dropna().std() / 2.0
            context.min_net.append(context.init_price)
    else:
        handle_net(context, context.min_net, 1, 7, context.securities[0], close)
        handle_net(context, context.mid_net, 2, 3, context.securities[0], close)
        handle_net(context, context.max_net, 3, 2, context.securities[0], close)

    context.pe_10year = context.pe_10year.iloc[1:]
    context.pe_10year = pd.concat([context.pe_10year, pd.Series([pe_ttm])])

    context.close_1year = context.close_1year.iloc[1:]
    context.close_1year = pd.concat([context.close_1year, pd.Series([pe_ttm])])

def handle_net(context, net, net_step, max_step, sec_code, close):
    
    last_buy = context.init_price
    if (net):
        last_min = net[-1]
    
    if close > last_buy + context.interval * net_step:
        if (len(net) == 0):
            return
        cnt = math.floor(context.value_size / close)
        lbt.order(context.securities[0], cnt, 'buy', 'close')
        del net[-1]
    
    if close < last_buy - context.interval * net_step:
        if (len(net) >= max_step):
            return
        cnt = math.floor(context.value_size / close)
        lbt.order(context.securities[0], cnt, 'sell', 'close')
        net.append(last_buy - context.interval * net_step)

    if (len(context.min_net) == 0 and len(context.mid_net) == 0 and len(context.max_net) == 0):
        context.start = False

def load_local_pe(index_name, start, end):
    file_name = './database/day/' + index_name + '.csv'
    if os.path.exists(file_name):
        df_table = pd.read_csv(file_name)
        df_table['date'] = df_table['date'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date())
        df_table.set_index('date', inplace=True)
        return df_table.loc[start:end]
    else:
        return pd.DataFrame()

lbt = LocalBacktest(init_func=initialize, handle_data_func=handle_data)
lbt.run()
display(lbt.summary_result())
lbt.plot()

