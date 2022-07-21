import imp
import datetime
import pandas as pd
import math

from evaluation.db import *
from evaluation.data import *

__all__ = ['update_to_lastest', 'local_recalculate']

def update_to_lastest(index_code, period='day'):
    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.datetime.now().date()
    if datetime.datetime.now().hour < 18:
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=-1)

    # 加载基础数据
    df_local = load_local_db(index_code, period)
    if len(df_local) <= 0:
        # 本地没有保存估值数据
        df_new = get_index_table(index_code, start_date, end_date, period)
        save_to_db(index_code, new=df_new, old=df_local, period=period)
    else:
        if period == 'month':
            if df_local.index[-1].strftime("%Y-%m") == end_date.strftime("%Y-%m"):
                df_local.drop([df_local.index[-1]], inplace=True)
        if df_local.index[-1] < end_date:
            df_new = get_index_table(index_code, df_local.index[-1] + datetime.timedelta(days=1), end_date, period)
            save_to_db(index_code, new=df_new, old=df_local, period=period)    
    df_local = load_local_db(index_code, period)
    if period == 'day':
        return doCalDay(index_code, df_local)
    if period == 'month':
        return doCalMonth(index_code, df_local)
    

def local_recalculate(index_code, period='day'):
    df_local = load_local_db(index_code, period)
    df_local.drop(df_local.columns[4:], axis=1, inplace=True)
    if period == 'day':
        return doCalDay(index_code, df_local)
    if period == 'month':
        return doCalMonth(index_code, df_local)


def doCalDay(index_code, df_local):
    number_per_year = 250
    # 基础数据加工
    for i in range(len(df_local.index)):
        if not 'close_5day_mean' in df_local.columns:
            df_local['close_5day_mean'] = pd.Series()
            df_local['close_10day_mean'] = pd.Series()
            df_local['close_20day_mean'] = pd.Series()
            df_local['close_1year_mean'] = pd.Series()

        if not math.isnan(df_local.close_5day_mean[i]):
            continue
        
        if i >= 4:
            df_local.close_5day_mean[i] = df_local.close[i - 4 : i + 1].mean()
                
        if i >= 9:
            df_local.close_10day_mean[i] = df_local.close[i - 9 : i + 1].mean()
                
        if i >= 19:
            df_local.close_20day_mean[i] = df_local.close[i - 19 : i + 1].mean()
        
        if i >= number_per_year - 1:
            df_local.close_1year_mean[i] = df_local.close[i - number_per_year + 1 : i + 1].mean()

        if (df_local.index[i].strftime("%d") == '01'):
            print(index_code + ' update to ' + df_local.index[i].strftime("%Y-%m-%d"))
    df_local = df_local.round(4)
    save_to_db(index_code, new=df_local, period='day')
    print(index_code + ' all finish')
    return df_local

def doCalMonth(index_code, df_local):
    number_per_year = 12
    # 基础数据加工
    for i in range(len(df_local.index)):
        if not 'pe_history_percent' in df_local.columns:
            df_local['pe_1year_percent'] = pd.Series()
            df_local['pe_3year_percent'] = pd.Series()
            df_local['pe_5year_percent'] = pd.Series()
            df_local['pe_10year_percent'] = pd.Series()
            df_local['pe_history_percent'] = pd.Series()
            df_local['pb_1year_percent'] = pd.Series()
            df_local['pb_3year_percent'] = pd.Series()
            df_local['pb_5year_percent'] = pd.Series()
            df_local['pb_10year_percent'] = pd.Series()
            df_local['pb_history_percent'] = pd.Series()

        if not math.isnan(df_local.pe_history_percent[i]):
            continue
         
        if i >= number_per_year - 1:
            df_local.pe_1year_percent[i] = calPrecent(df_local.pe[i - number_per_year + 1 : i+1])
            
        if i >= number_per_year * 3 - 1:
            df_local.pe_3year_percent[i] = calPrecent(df_local.pe[i - number_per_year * 3 + 1: i+1])
            
        if i >= number_per_year * 5 - 1:
            df_local.pe_5year_percent[i] = calPrecent(df_local.pe[i - number_per_year * 5 + 1: i+1])
                
        if i >= number_per_year * 10 - 1:
            df_local.pe_10year_percent[i] = calPrecent(df_local.pe[i - number_per_year * 10 + 1 : i+1])
            
        df_local.pe_history_percent[i] = calPrecent(df_local.pe[0:i+1])
                
        if i >= number_per_year - 1:
            df_local.pb_1year_percent[i] = calPrecent(df_local.pb[i - number_per_year + 1: i+1])
            
        if i >= number_per_year * 3 - 1:
            df_local.pb_3year_percent[i] = calPrecent(df_local.pb[i - number_per_year * 3 + 1: i+1])
            
        if i >= number_per_year * 5 - 1:
            df_local.pb_5year_percent[i] = calPrecent(df_local.pb[i - number_per_year * 5 + 1: i+1])
                
        if i >= number_per_year * 10 - 1:
            df_local.pb_10year_percent[i] = calPrecent(df_local.pb[i - number_per_year * 10 + 1: i+1])
            
        df_local.pb_history_percent[i] = calPrecent(df_local.pb[0:i+1])
        
        if (df_local.index[i].strftime("%d") == '01'):
            print(index_code + ' update to ' + df_local.index[i].strftime("%Y-%m-%d"))
    df_local = df_local.round(4)
    save_to_db(index_code, new=df_local, period='month')
    print(index_code + ' all finish')
    return df_local
    
def calPrecent(df_pe):
    now=df_pe[-1]
    cnt = 0.0
    for i in range(len(df_pe)):
        if now > df_pe[i]:
            cnt = cnt + 1
        if now == df_pe[i]:
            cnt = cnt + 0.5
    return cnt / len(df_pe)