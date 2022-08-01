from WindPy import w
w.start()

error, df = w.wsd("510330.SH",  "pe_ttm",  "ED-10TD",  "2022-07-24",  "", usedf=True);

print(df)