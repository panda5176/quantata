from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, wait
import pandas as pd
import yfinance as yf

TIME = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
TODAY = datetime.today()

# http://data.krx.co.kr/
df = pd.read_csv("data/data_5939_20220827.csv", encoding="cp949")
symbols = list()
for _, row in df.iterrows():
    symbol, market = row[1], row["시장구분"]
    if market == "KOSPI":
        symbol += ".KS"
    elif market == "KOSDAQ":
        symbol += ".KQ"
    else:
        continue
    symbols.append(symbol)

# # https://www.nasdaq.com/market-activity/stocks/screener
df = pd.read_csv("data/nasdaq_screener_1661518383831.csv")
symbols += df.Symbol.tolist()

print(len(symbols))

thread_pool_executor = ThreadPoolExecutor(max_workers=4)


def process(writer, symbol):
    print(f"\n{symbol} try")
    ticker = yf.Ticker(symbol)

    if len(ticker.quarterly_financials.columns) < 2:
        return

    for quarter in range(1, len(ticker.quarterly_financials.columns)):
        closing_day_raw = ticker.quarterly_financials.columns[quarter]
        closing_day_after_1q_raw = ticker.quarterly_financials.columns[
            quarter - 1
        ]

        try:
            if not (
                TODAY
                >= closing_day_after_1q_raw
                > closing_day_raw
                >= TODAY - timedelta(365)
            ) or not (
                closing_day_raw + timedelta(120)
                >= closing_day_after_1q_raw
                > closing_day_raw
            ):
                continue
        except TypeError:
            continue

        closing_day = closing_day_raw.strftime("%Y-%m-%d")
        date_offset, no_history_count, no_history = 1, 0, False
        while True:
            next_day = (closing_day_raw + pd.DateOffset(date_offset)).strftime(
                "%Y-%m-%d"
            )
            try:
                share_price = ticker.history(
                    start=closing_day, end=next_day
                ).Close[0]
                break
            except IndexError:
                date_offset += 1
                no_history_count += 1
                if no_history_count == 10:
                    no_history = True
                    break

        if no_history:
            continue

        closing_day_after_1q = closing_day_after_1q_raw.strftime("%Y-%m-%d")
        date_offset, no_history_count, no_history = 1, 0, False
        while True:
            next_day_after_1q = (
                closing_day_after_1q_raw + pd.DateOffset(date_offset)
            ).strftime("%Y-%m-%d")
            try:
                share_price_after_1q = ticker.history(
                    start=closing_day_after_1q, end=next_day_after_1q
                ).Close[0]
                break
            except IndexError:
                date_offset += 1
                no_history_count += 1
                if no_history_count == 10:
                    no_history = True
                    break

        if no_history:
            continue

        try:
            share_count = ticker.info["sharesOutstanding"]
            market_capital = share_price * share_count
            net_worth = ticker.quarterly_balancesheet.loc[
                "Total Stockholder Equity"
            ][0]
            net_income = ticker.quarterly_financials.loc["Net Income"][0]
            total_assets = ticker.quarterly_balancesheet.loc["Total Assets"][0]
            total_revenue = ticker.quarterly_financials.loc["Total Revenue"][0]
            total_cash = ticker.quarterly_balancesheet.loc["Cash"][0]
            total_liabilities = ticker.quarterly_balancesheet.loc["Total Liab"][
                0
            ]

            gross_profit = ticker.quarterly_financials.loc["Gross Profit"][0]
            operating_cashflow = ticker.quarterly_cashflow.loc[
                "Total Cash From Operating Activities"
            ][0]
            enterprise_value = market_capital + total_liabilities - total_cash
            earnings_before_interest = ticker.quarterly_financials.loc["Ebit"][
                0
            ]
            operating_income = ticker.quarterly_financials.loc[
                "Operating Income"
            ][0]
            current_liabilities = ticker.quarterly_balancesheet.loc[
                "Total Current Liabilities"
            ][0]
            employed_capital = total_assets - current_liabilities

            net_income_before_1q = ticker.quarterly_financials.loc[
                "Net Income"
            ][1]
            net_income_1y = ticker.financials.loc["Net Income"][0]
            net_income_before_1y = ticker.financials.loc["Net Income"][1]
            total_revenue_before_1q = ticker.quarterly_financials.loc[
                "Total Revenue"
            ][1]
            total_revenue_1y = ticker.financials.loc["Total Revenue"][0]
            total_revenue_before_1y = ticker.financials.loc["Total Revenue"][1]
            total_assets_before_1q = ticker.quarterly_balancesheet.loc[
                "Total Assets"
            ][1]
            total_assets_1y = ticker.balancesheet.loc["Total Assets"][0]
            total_assets_before_1y = ticker.balancesheet.loc["Total Assets"][1]

            pe_ratio = market_capital / net_income
            pb_ratio = market_capital / net_worth
            ps_ratio = market_capital / total_revenue
            pcf_ratio = market_capital / operating_cashflow
            ev_ebit_ratio = enterprise_value / earnings_before_interest
            ev_sales_ratio = enterprise_value / total_revenue
            roe_ratio = net_income / net_worth
            roa_ratio = net_income / total_assets
            gpa_ratio = gross_profit / total_assets
            la_ratio = total_liabilities / total_assets
            turnover_ratio = total_revenue / total_assets
            gross_margin = gross_profit / total_revenue
            gross_operating_margin = operating_income / total_revenue
            net_profit_margin = net_income / total_revenue
            roc_ratio = earnings_before_interest / employed_capital

            income_growth_1q = (
                net_income - net_income_before_1q
            ) / net_income_before_1q
            income_growth_1y = (
                net_income_1y - net_income_before_1y
            ) / net_income_before_1y
            revenue_growth_1q = (
                total_revenue - total_revenue_before_1q
            ) / total_revenue_before_1q
            revenue_growth_1y = (
                total_revenue_1y - total_revenue_before_1y
            ) / total_revenue_before_1y
            assets_growth_1q = (
                total_assets - total_assets_before_1q
            ) / total_assets_before_1q
            assets_growth_1y = (
                total_assets_1y - total_assets_before_1y
            ) / total_assets_before_1y

            share_price_growth = (
                share_price_after_1q - share_price
            ) / share_price

        except (ZeroDivisionError, TypeError, IndexError, KeyError):
            continue

        row = [
            symbol,
            closing_day,
            next_day,
            share_price,
            closing_day_after_1q,
            next_day_after_1q,
            share_price_after_1q,
            share_count,
            market_capital,
            net_worth,
            net_income,
            total_assets,
            total_revenue,
            total_cash,
            total_liabilities,
            gross_profit,
            operating_cashflow,
            operating_income,
            enterprise_value,
            earnings_before_interest,
            current_liabilities,
            employed_capital,
            net_income_1y,
            net_income_before_1q,
            net_income_before_1y,
            total_revenue_1y,
            total_revenue_before_1q,
            total_revenue_before_1y,
            total_assets_1y,
            total_assets_before_1q,
            total_assets_before_1y,
            pe_ratio,
            pb_ratio,
            ps_ratio,
            pcf_ratio,
            ev_ebit_ratio,
            ev_sales_ratio,
            roe_ratio,
            roa_ratio,
            gpa_ratio,
            la_ratio,
            turnover_ratio,
            gross_margin,
            gross_operating_margin,
            net_profit_margin,
            roc_ratio,
            income_growth_1q,
            income_growth_1y,
            revenue_growth_1q,
            revenue_growth_1y,
            assets_growth_1q,
            assets_growth_1y,
            share_price_growth,
        ]
        writer.write("\t".join(list(map(str, row))) + "\n")
        print(f"\n{symbol} {quarter+1}Q done")


data = list()
with open(f"data/{TIME}.tsv", "w") as writer:
    columns = [
        "Symbol",
        "ClosingDay",
        "NextDay",
        "SharePrice",
        "ClosingDayAfter1Q",
        "NextDayAfter1Q",
        "SharePriceAfter1Q",
        "ShareCount",
        "MarketCapital",
        "NetWorth",
        "NetIncome",
        "TotalAssets",
        "TotalRevenue",
        "TotalCash",
        "TotalLiabilities",
        "GrossProfit",
        "OperatingCashflow",
        "OperatingIncome",
        "EnterpriseValue",
        "EarningsBeforeInterest",
        "CurrentLiabilities",
        "EmployedCapital",
        "NetIncome1Y",
        "NetIncomeBefore1Q",
        "NetIncomeBefore1Y",
        "TotalRevenue1Y",
        "TotalRevenueBefore1Q",
        "TotalRevenueBefore1Y",
        "TotalAssets1Y",
        "TotalAssetsBefore1Q",
        "TotalAssetsBefore1Y",
        "PERatio",
        "PBRatio",
        "PSRatio",
        "PCFRatio",
        "EVEBITRatio",
        "EVSalesRatio",
        "ROERatio",
        "ROARatio",
        "GPARatio",
        "LARatio",
        "TurnoverRatio",
        "GrossMargin",
        "GrossOperatingMargin",
        "NetProfitMargin",
        "ROCRatio",
        "IncomeGrowth1Q",
        "IncomeGrowth1Y",
        "RevenueGrowth1Q",
        "RevenueGrowth1Y",
        "AssetsGrowth1Q",
        "AssetsGrowth1Y",
        "SharePriceGrowth",
    ]
    writer.write("\t".join(columns) + "\n")

    futures = list()
    for symbol in symbols:
        futures.append(thread_pool_executor.submit(process, writer, symbol))
    wait(futures)
