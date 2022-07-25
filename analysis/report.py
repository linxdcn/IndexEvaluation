import pandas as pd
import datetime
from evaluation import *

indexs = interested_index

df = pd.DataFrame(columns=['name', 'pe', 'pe_3year_percent', 'pe_5year_percent', 'pe_10year_percent', 'pe_history_percent'])
df.set_index(['name'], inplace=True)

for index in indexs:
    df_local = load_local_db(index, 'month')
    row = df_local.iloc[len(df_local) - 1]
    df.loc[indexs[index]] = [
        row['pe'],
        row['pe_3year_percent'],
        row['pe_5year_percent'],
        row['pe_10year_percent'],
        row['pe_history_percent'],
    ]

file_name = './database/report/' + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
df.to_csv(file_name)
