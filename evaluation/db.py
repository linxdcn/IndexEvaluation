import os
import datetime
import pandas as pd
from evaluation.data import *

__all__ = [
    'load_local_db',
    'load_local_db_by_filename', 
    'save_to_db',
    'load_position',
    ]

database_path = './database/'

def load_local_db(index_code, period='day'):
    file_name = database_path + period + "/" + get_index_name(index_code) + '.csv'
    if os.path.exists(file_name):
        df_table = pd.read_csv(file_name)
        df_table['date'] = df_table['date'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date())
        df_table.set_index('date', inplace=True)
        return df_table
    else:
        return pd.DataFrame()

def load_local_db_by_filename(filename, period='day'):
    file_name = database_path + period + "/" + filename + '.csv'
    if os.path.exists(file_name):
        df_table = pd.read_csv(file_name)
        df_table['date'] = df_table['date'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date())
        df_table.set_index('date', inplace=True)
        return df_table
    else:
        return pd.DataFrame()

def save_to_db(index_code, new, old=pd.DataFrame(), period='day'):
    file_name = database_path + period + "/" + get_index_name(index_code) + '.csv'
    if len(old) <= 0:
        new.to_csv(file_name)
    else:
        df = old.append(new)
        df.to_csv(file_name)

def load_position(cash):
    file_name = database_path + "position/trade.csv"

    def cal_position(df, df_nav):
        position = 0;
        for i in range(len(df)):
            p = df.iloc[i].quantity * df_nav.loc[df.iloc[i].code, 'nav']
            if df.iloc[i].side == 'buy':
                position += p
            else:
                position -= p

        return round(position, 2)

    if os.path.exists(file_name):
        df = pd.read_csv(file_name)

        indexs = list(df.groupby(['code']).count().index)
        df_nav = get_index_nav(indexs)
        df = df.groupby(['L1', 'L2', 'L3']).apply(lambda x: cal_position(x, df_nav))
        df = df.reset_index()
        df.columns = ['L1', 'L2', 'L3', 'position']
        df.sort_values(by=['L1', 'L2', 'L3'], ascending=[True, True, True], inplace=True)
        df.loc[len(df)]=[ '现金', '现金', '现金', cash ]
        return df
    else:
        return pd.DataFrame()