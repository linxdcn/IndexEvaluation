from evaluation import *

# update_to_lastest('000985.CSI', 'day')
# update_to_lastest('HSI.HI', 'day')
# update_to_lastest('SPX.GI', 'day')
# update_to_lastest('NDX.GI', 'day')

df_local = load_local_db('000985.CSI', 'day')
df_local = df_local.iloc[-2500:]
pe = df_local.pe[-1]
pe_percent = df_local.pe.loc[df_local.pe < pe].count() / df_local.pe.count()
print(pe_percent)