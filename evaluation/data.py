from WindPy import *
w.start()

__all__ = ['get_index_table', 'get_index_name']

def get_index_table(index_code, start_date, end_date):
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    error, df = w.wsd(index_code, "close,pe_ttm,pb_lf,dividendyield2", start_str, end_str, "", usedf=True)
    if start_str == end_str:
        df['date'] = [start_date]
        df.set_index(['date'], inplace=True)
    df.index.names = ['date']
    df.columns = df.columns.map(lambda x : x.lower())
    df.dropna(inplace=True)
    if df.empty:
        return df
    df = df.round(4)
    return df

def get_index_name(index_code):
    error, df = w.wss(index_code, "SEC_NAME", usedf=True)
    df.columns = df.columns.map(lambda x : x.lower())
    return df.sec_name[index_code]