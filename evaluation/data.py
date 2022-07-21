import pandas as pd

from WindPy import *
w.start()

__all__ = ['get_index_table', 'get_index_name']

wind_init = False
wind_datasource = any

def get_index_table(index_code, start_date, end_date, period='day'):
    init_wind()
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    options = ""
    if period == 'month':
        options = 'Period=M'
    error, df = wind_datasource.wsd(index_code, "close,pe_ttm,pb_lf,dividendyield2", start_str, end_str, options, usedf=True)
    if error != 0:
        return pd.DataFrame()
    if df.shape[0] == 1:
        df['date'] = [end_str]
        df.set_index(['date'], inplace=True)
    df.index.names = ['date']
    df.columns = df.columns.map(lambda x : x.lower())
    df.rename(columns={'pe_ttm':'pe', 'pb_lf':'pb', 'dividendyield2' : 'dividend'}, inplace=True)
    df.dropna(inplace=True)
    if df.empty:
        return df
    df = df.round(4)
    return df

def get_index_name(index_code):
    init_wind()
    error, df = wind_datasource.wss(index_code, "SEC_NAME", usedf=True)
    if error != 0:
        return index_code
    df.columns = df.columns.map(lambda x : x.lower())
    return df.sec_name[index_code]

def init_wind():
    global wind_init
    global wind_datasource
    if not wind_init:
        from WindPy import w
        w.start()
        wind_init = True
        wind_datasource = w