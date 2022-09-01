import pandas as pd
import numpy as np
import datetime as dt
import os

from localbacktest.common import LbtConfig

wind_init = False
wind_datasource = any
jq_init = False

__all__ = ['get_market_data']

def get_market_data(security, start_date, end_date, fields=['open', 'close', 'pre_close']):
    '''get_market_data

    接入数据源要求:
    * 价格为前复权数据
    * 日期序列为交易日，包括停牌日期
    * 停牌数据用np.nan填充

    Args:
        security (list): 后缀说明: 上交所,SH; 深交所,SZ; 北交所,BJ
        start_date (str): '2020-09-01'
        end_date (str): '2020-09-01'
        fields

    Returns:
        DataFrame: a multiIndex Daframe, a simple example:
                                    open  close  pre_close
            security    datetime                           
            603990.SH   2021-12-21  20.61  20.82      20.74
                        2021-12-22  20.72  20.57      20.82
                        2021-12-23  20.50  20.16      20.57
            600030.SH   2021-12-21  25.83  26.11      25.88
                        2021-12-22  26.12  25.88      26.11
                        2021-12-23  25.91  25.93      25.88
    '''
    if LbtConfig.get_datasource() == 'wind':
        return __get_from_wind(security, start_date, end_date)
    elif LbtConfig.get_datasource() == 'jq':
        return __get_from_joinquant(security, start_date, end_date)
    elif LbtConfig.get_datasource() == 'local':
        return __get_from_wind_with_cache(security, start_date, end_date)
    else:
        return None

def __get_from_wind(security, start_date, end_date):
    global wind_init
    global wind_datasource
    if not wind_init:
        from WindPy import w
        w.start()
        wind_init = True
        wind_datasource = w
    
    if (len(security) == 1):
        error, result = wind_datasource.wsd(security, 'open,close,pre_close', start_date, end_date, "PriceAdj=F", usedf=True)
        if error != 0:
            return pd.DataFrame()
        if len(result) == 1:
            return pd.DataFrame()
        result.columns = [s.lower() for s in result.columns]
        result['security'] = security[0]
        result['datetime'] = result.index
        result.set_index(['security', 'datetime'], inplace=True)
        return result
    else:
        result = pd.DataFrame(columns=['datetime', 'security', 'open', 'close', 'pre_close'])
        for col in ['open', 'close', 'pre_close']:
            error, data = wind_datasource.wsd(security, col, start_date, end_date, "PriceAdj=F;Fill=Blank", usedf=True)
            idx = 0
            row = len(data)
            for s in data.columns:
                for i in range(row):
                    if col == 'open':
                        result.loc[idx, 'datetime'] = data.index[i]
                        result.loc[idx, 'security'] = s
                    result.loc[idx, col] = data[s].iloc[i]
                    idx += 1
        result.set_index(['security', 'datetime'], inplace=True)
        result.replace(0, np.nan, inplace=True)
        return result

    

def __get_from_joinquant(security, start_date, end_date):
    global jq_init
    from jqdatasdk import auth, get_price
    if not jq_init:
        auth(LbtConfig.get_jq_user(), LbtConfig.get_jq_password())
        jq_init = True
    to_jqcode = lambda s : s.replace('SH', 'XSHG').replace('SZ', 'XSHE')
    from_fqcode = lambda s : s.replace('XSHG', 'SH').replace('XSHE', 'SZ')
    new_security = [to_jqcode(s) for s in security]
    result = get_price(new_security, start_date, end_date, fields=['open', 'close', 'pre_close'], panel=False, fill_paused=False)
    result.rename(columns={"time": "datetime", "code": "security"}, inplace=True)
    result['security'] = result['security'].apply(from_fqcode)
    result.set_index(['security', 'datetime'], inplace=True)
    result.replace(0, np.nan, inplace=True)
    return result

def __get_from_wind_with_cache(security, start_date, end_date):    
    if len(security) > 1:
        raise Exception('not support multi security')

    code = security[0]
    input_start = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    input_end = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    
    d_start = dt.date(2000, 1, 1)
    d_end = dt.datetime.now().date()
    if dt.datetime.now().hour < 18:
        d_end = dt.datetime.now().date() + dt.timedelta(days=-1)
    
    df_local = __load_cache(code)
    
    if len(df_local) <= 0:
        # 本地没有保存估值数据
        df_new = __get_from_wind(security, d_start.strftime("%Y-%m-%d"), d_end.strftime("%Y-%m-%d"))
        __save_cache(code, new=df_new, old=df_local)
    else:
        if df_local.index[-1][1] < d_end:
            tmp_start = df_local.index[-1][1] + dt.timedelta(days=1)
            df_new = __get_from_wind(security, tmp_start.strftime("%Y-%m-%d"), d_end.strftime("%Y-%m-%d"))
            __save_cache(code, new=df_new, old=df_local)    
    df_local = __load_cache(code)
    df_local = df_local.loc[code].loc[input_start : input_end]
    df_local.reset_index(inplace=True)
    df_local['security'] = code
    return df_local.set_index(['security', 'datetime'])

def __load_cache(index_code):
    file_name = './database/backtest/' + index_code + '.csv'
    if os.path.exists(file_name):
        df_table = pd.read_csv(file_name)
        df_table['datetime'] = df_table['datetime'].apply(lambda x: dt.datetime.strptime(x, "%Y-%m-%d").date())
        df_table.set_index(['security', 'datetime'], inplace=True)
        return df_table
    else:
        return pd.DataFrame()

def __save_cache(index_code, new, old=pd.DataFrame()):
    file_name = './database/backtest/' + index_code + '.csv'
    if len(old) <= 0:
        new.to_csv(file_name)
    else:
        df = old.append(new)
        df.to_csv(file_name)
