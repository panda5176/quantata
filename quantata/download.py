import pandas as pd
import yfinance as yf
from tqdm import tqdm

# # http://data.krx.co.kr/
# df = pd.read_csv("data_3258_20220826.csv", encoding="cp949")

# symbols_kr = list()
# for _, row in df.iterrows():
#     symbol, market = row[1], row["시장구분"]
#     if market == "KOSPI":
#         symbol += ".KS"
#     elif market == "KOSDAQ":
#         symbol += ".KQ"
#     else:
#         continue
#     symbols_kr.append(symbol)
# print(len(symbols_kr))

# https://www.nasdaq.com/market-activity/stocks/screener
df = pd.read_csv("data/nasdaq_screener_1661518383831.csv")
for symbol in tqdm(df.Symbol[:3]):
    new_df = yf.Ticker(symbol).quarterly_financials
    new_df.to_csv(f"data/{symbol}.tsv", sep="\t")

