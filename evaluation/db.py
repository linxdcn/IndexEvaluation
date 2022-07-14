import os
import datetime
import pandas as pd
from evaluation.data import get_index_name

__all__ = ['load_local_db', 'save_to_db']

database_path = './database/'

def load_local_db(index_code):
    file_name = database_path + get_index_name(index_code) + '.csv'
    if os.path.exists(file_name):
        df_table = pd.read_csv(file_name)
        df_table['date'] = df_table['date'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date())
        df_table.set_index('date', inplace=True)
        return df_table
    else:
        return pd.DataFrame()

def save_to_db(index_code, new, old=pd.DataFrame()):
    file_name = database_path + get_index_name(index_code) + '.csv'
    if len(old) <= 0:
        new.to_csv(file_name)
    else:
        df = old.append(new)
        df.to_csv(file_name)