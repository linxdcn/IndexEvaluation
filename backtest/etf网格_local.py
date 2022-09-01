from json import load
from localbacktest import *
LbtConfig.set_datasource('local')

from IPython.display import display
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import os
import math

#标的
#name,etf,index
#沪深300,510330.SH,000300.SH
#中证500,510500.SH,000905.SH
#上证50,510050.SH,000016.SH
#证券公司,512000.SH,399975.SZ
#全指金融地产,159940.SZ,000992.SH
#创业板指,159915.SZ,399006.SZ,
#创业板50,159949.SZ,399673.SZ
#恒生指数,159920.SZ,HSI.HI
def initialize(context):

    context.index = '沪深300'
    context.securities = ['510330.SH']
    context.benchmark = '000300.SH'
    context.type = 'pe'

    # 候选
    context.index = '中证500'
    context.securities = ['510500.SH']
    context.benchmark = '000905.SH'
    context.type = 'pe'

    # context.index = '上证50'
    # context.securities = ['510050.SH']
    # context.benchmark = '000016.SH'
    # context.type = 'pb'

    # 候选
    # context.index = '证券公司'
    # context.securities = ['512000.SH']
    # context.benchmark = '399975.SZ'
    # context.type = 'pb'

    # context.index = '全指金融地产'
    # context.securities = ['159940.SZ']
    # context.benchmark = '000992.SH'
    # context.type = 'pe'

    # 候选
    # context.index = '创业板指'
    # context.securities = ['159915.SZ']
    # context.benchmark = '399006.SZ'
    # context.type = 'pe'

    # 候选
    # context.index = '创业板50'
    # context.securities = ['159949.SZ']
    # context.benchmark = '399673.SZ'
    # context.type = 'pe'

    # context.index = '恒生指数'
    # context.securities = ['159920.SZ']
    # context.benchmark = 'HSI.HI'
    # context.type = 'pe'

    context.start_date = '2016-01-01'
    context.end_date = '2022-07-01'
    context.capital = 100000
    context.commission = 0.00025

    startd = datetime.datetime.strptime(context.start_date, "%Y-%m-%d").date()
    oneday_befor_startd = startd-relativedelta(days=1)

    df = load_local_pe(context.index, oneday_befor_startd-relativedelta(years=10), oneday_befor_startd)
    context.pe_10year = df[context.type]

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

    context.value_size = context.capital / 10

    context.min_net = []
    context.mid_net = []
    context.max_net = []

    context.min_cnt = []
    context.mid_cnt = []
    context.max_cnt = []

def handle_data(bar_datetime, context, bar_data):

    pe_ttm = context.pe_all.loc[bar_datetime.date(), context.type]
    close = context.security_all.loc[context.securities[0]].loc[bar_datetime.date(), 'close']
    if math.isnan(close):
        return

    if not context.start:
        pe_percent = context.pe_10year.loc[context.pe_10year < pe_ttm].count() / context.pe_10year.count()
        interval = context.close_1year.dropna().std() / 3.0
        step_percent = interval / close
        if pe_percent < 0.4:
            interval = close * 0.05
            context.start = True
            context.init_price = close
            context.interval = interval
            context.min_net.append(context.init_price)

            cnt = math.floor(context.value_size / close)
            context.min_cnt.append(cnt)

            lbt.order(context.securities[0], cnt, 'buy', 'close')
            print('{0} start net, interval: {1}, step_percent: {2}, pe_percent: {3}'
                .format(bar_datetime.strftime("%Y-%m-%d"), 
                round(context.interval, 2), 
                round(context.interval / close, 2), 
                round(pe_percent, 2)))
            print('buy {0} with {1} at {2}'.format(cnt, close, bar_datetime.strftime("%Y-%m-%d")))
        if pe_percent > 0.75:
            cnt = lbt.getPosition(context.securities[0])
            if cnt > 0:
                lbt.order(context.securities[0], cnt, 'sell', 'close')
                print('sell all, cnt={0}, close={1}, date={2}'.format(cnt, close, bar_datetime.strftime("%Y-%m-%d")))        
    else:
        handle_net(context, context.min_net, context.min_cnt, 1, 8, context.securities[0], close, bar_datetime)
        handle_net(context, context.mid_net, context.mid_cnt, 2, 4, context.securities[0], close, bar_datetime)
        handle_net(context, context.max_net, context.max_cnt, 4, 2, context.securities[0], close, bar_datetime)

    if (len(context.pe_10year) > 2500):
        context.pe_10year = context.pe_10year.iloc[1:]
    context.pe_10year = pd.concat([context.pe_10year, pd.Series([pe_ttm])])

    if (len(context.close_1year) > 250):
        context.close_1year = context.close_1year.iloc[1:]
    context.close_1year = pd.concat([context.close_1year, pd.Series([pe_ttm])])

def handle_net(context, net, net_cnt, net_step, max_step, sec_code, close, bar_datetime):
    
    last_buy = context.init_price
    if (net):
        last_buy = net[-1]
    
    if close > last_buy + context.interval * net_step:
        if (len(net) == 0):
            return
        # 留利润
        # cnt = net_cnt[-1]
        cnt = math.floor(context.value_size / close)
        lbt.order(context.securities[0], cnt, 'sell', 'close')
        print('sell {0} with {1} at {2}'.format(cnt, close, bar_datetime.strftime("%Y-%m-%d")))
        del net[-1]
        del net_cnt[-1]
    
    if close < last_buy - context.interval * net_step:
        if (len(net) >= max_step):
            return
        cnt = math.floor(context.value_size / close)
        lbt.order(context.securities[0], cnt, 'buy', 'close')
        print('buy {0} with {1} at {2}'.format(cnt, close, bar_datetime.strftime("%Y-%m-%d")))
        net.append(last_buy - context.interval * net_step)
        net_cnt.append(cnt)

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

