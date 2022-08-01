
# import datetime
# from dateutil.relativedelta import relativedelta
# import pandas as pd

# from WindAlgo import *
# from WindPy import w
# w.start()

# def initialize(context):# 定义初始化函数
#     context.capital = 1200000
    
#     context.securities = ["510500.SH"]
#     context.benchmark = '000905.SH'
#     context.index = context.benchmark
#     context.start_date = "20160101"
#     context.end_date = "20220701"
#     context.period = 'd'

#     sd = datetime.datetime.strptime(context.start_date, "%Y%m%d")
#     sd = sd-relativedelta(days=1)
#     end_str = sd.strftime("%Y-%m-%d")

#     error, df = w.wsd(context.index,  "pe_ttm",  "ED-10Y",  end_str,  "", usedf=True)
#     if error != 0:
#         print(error)
#     else:
#         print(df)
#     context.pe_10year = df['PE_TTM']

#     error, df = w.wsd(context.securities[0],  "close",  "ED-1Y",  end_str,  "", usedf=True)
#     if error != 0:
#         print(error)
#     else:
#         print(df)
#     context.close_1year = df['CLOSE']

#     start_str = datetime.datetime.strptime(context.start_date, "%Y%m%d").strftime("%Y-%m-%d")
#     end_str = datetime.datetime.strptime(context.end_date, "%Y%m%d").strftime("%Y-%m-%d")
#     error, df = w.wsd(context.index,  "pe_ttm",  start_str,  end_str,  "", usedf=True)
#     if error != 0:
#         print(error)
#     else:
#         print(df)
#     context.pe_all = df

#     context.start = False
#     context.init_price = 0
#     context.interval = 0

#     context.value_size = context.capital / 12

#     context.min_net = []
#     context.mid_net = []
#     context.max_net = []

# def handle_data(bar_datetime, context, bar_data):

#     date_str = bar_datetime.strftime("%Y%m%d")
#     pe_ttm = context.pe_all.loc[bar_datetime.date(), 'PE_TTM']
#     close = bar_data[context.securities[0]]['open']

#     if not context.start:
#         print('{0},{1}'.format(pe_ttm, context.pe_10year.dropna().mean()))
#         if pe_ttm < context.pe_10year.dropna().mean():
#             context.start = True
#             context.init_price = close
#             context.interval = context.close_1year.dropna().std() / 2.0
#             context.min_net.append(context.init_price)
#     else:
#         handle_net(context, context.min_net, 1, 7, context.securities[0], close)
#         handle_net(context, context.mid_net, 2, 3, context.securities[0], close)
#         handle_net(context, context.max_net, 3, 2, context.securities[0], close)

#     context.pe_10year = context.pe_10year.iloc[1:]
#     context.pe_10year = pd.concat([context.pe_10year, pd.Series([pe_ttm])])

#     context.close_1year = context.close_1year.iloc[1:]
#     context.close_1year = pd.concat([context.close_1year, pd.Series([pe_ttm])])

# def handle_net(context, net, net_step, max_step, sec_code, close):
    
#     last_buy = context.init_price
#     if (net):
#         last_min = net[-1]
    
#     if close > last_buy + context.interval * net_step:
#         if (len(net) == 0):
#             return
#         bkt.order_value(sec_code, context.value_size, 'sell', 'close')
#         del net[-1]
    
#     if close < last_buy - context.interval * net_step:
#         if (len(net) >= max_step):
#             return
#         bkt.order_value(sec_code, context.value_size, 'buy', 'close')
#         net.append(last_buy - context.interval * net_step)

#     if (len(context.min_net) == 0 and len(context.mid_net) == 0 and len(context.max_net) == 0):
#         context.start = False

# bkt = BackTest(init_func = initialize, handle_data_func=handle_data)
# res = bkt.run()

# from localbacktest import *
# LbtConfig.set_datasource('local')

# df = get_market_data(["600030.SH"], "2019-01-10", "2019-01-11")
# print(df)