import imp
import datetime
import pandas as pd
import math

from evaluation.db import *
from evaluation.data import *

__all__ = ['update_to_lastest']

days_per_year = 250

def update_to_lastest(index_code):
    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.datetime.now().date()

    # 加载基础数据
    df_local = load_local_db(index_code)
    if len(df_local) <= 0:
        # 本地没有保存估值数据
        df_new = get_index_table(index_code, start_date, end_date)
        save_to_db(index_code, new=df_new, old=df_local)
    else:
        if df_local.index[-1] < end_date:
            df_new = get_index_table(index_code, df_local.index[-1] + datetime.timedelta(days=1), end_date)
            save_to_db(index_code, new=df_new, old=df_local)    
    df_local = load_local_db(index_code)
    
    # 基础数据加工
    for i in range(len(df_local.index)):
        if not 'pe_history_percent' in df_local.columns:
            df_local['pe_5day_mean'] = pd.Series()
            df_local['pe_10day_mean'] = pd.Series()
            df_local['pe_20day_mean'] = pd.Series()
            df_local['pe_1year_mean'] = pd.Series()
            df_local['pe_3year_mean'] = pd.Series()
            df_local['pe_5year_mean'] = pd.Series()
            df_local['pe_10year_mean'] = pd.Series()
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
        
        if i >= 5:
            df_local.pe_5day_mean[i] = df_local.pe[i - 5 : i].mean()
            
        if i >= 10:
            df_local.pe_10day_mean[i] = df_local.pe[i - 10 : i].mean()
            
        if i >= 20:
            df_local.pe_20day_mean[i] = df_local.pe[i - 20 : i].mean()
        
        if i >= days_per_year:
            df_local.pe_1year_mean[i] = df_local.pe[i - days_per_year : i].mean()
            
        if i >= days_per_year * 3:
            df_local.pe_3year_mean[i] = df_local.pe[i - days_per_year * 3 : i].mean()
            
        if i >= days_per_year * 5:
            df_local.pe_5year_mean[i] = df_local.pe[i - days_per_year * 5 : i].mean()
    
        if i >= days_per_year * 10:
            df_local.pe_10year_mean[i] = df_local.pe[i - days_per_year * 10 : i].mean()
            
        if i >= days_per_year:
            df_local.pe_1year_percent[i] = calPrecent(df_local.pe[i - days_per_year : i+1])
        
        if i >= days_per_year * 3:
            df_local.pe_3year_percent[i] = calPrecent(df_local.pe[i - days_per_year * 3 : i+1])
          
        if i >= days_per_year * 5:
            df_local.pe_5year_percent[i] = calPrecent(df_local.pe[i - days_per_year * 5 : i+1])
            
        if i >= days_per_year * 10:
            df_local.pe_10year_percent[i] = calPrecent(df_local.pe[i - days_per_year * 10 : i+1])
          
        df_local.pe_history_percent[i] = calPrecent(df_local.pe[0:i+1])
            
        if i >= days_per_year:
            df_local.pb_1year_percent[i] = calPrecent(df_local.pb[i - days_per_year : i+1])
        
        if i >= days_per_year * 3:
            df_local.pb_3year_percent[i] = calPrecent(df_local.pb[i - days_per_year * 3 : i+1])
          
        if i >= days_per_year * 5:
            df_local.pb_5year_percent[i] = calPrecent(df_local.pb[i - days_per_year * 5 : i+1])
            
        if i >= days_per_year * 10:
            df_local.pb_10year_percent[i] = calPrecent(df_local.pb[i - days_per_year * 10 : i+1])
        
        df_local.pb_history_percent[i] = calPrecent(df_local.pb[0:i+1])
        
        if (df_local.index[i].strftime("%d") == '01'):
            print(index_code + ' update to ' + df_local.index[i].strftime("%Y-%m-%d"))
    df_local = df_local.round(4)
    save_to_db(index_code, new=df_local)
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