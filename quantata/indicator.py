import numpy as np


def calc_ma(prices, window=3):
    mas = list()
    for day, price in enumerate(prices):
        if day < window - 1:
            mas.append(price)
        else:
            mas.append(np.average(prices[day - window + 1 : day + 1]))
    return np.array(mas)


def calc_ema(prices, period=3):
    emas = list()
    alpha = 2 / (period + 1)
    for day, price in enumerate(prices):
        if not day:
            emas.append(price)
        else:
            emas.append(alpha * price + (1 - alpha) * emas[-1])
    return np.array(emas)


def calc_macd(prices, short_period=12, long_period=26):
    return calc_ema(prices, short_period) - calc_ema(prices, long_period)


def calc_macd_signal(prices, short_period=12, long_period=26, signal_period=9):
    macds = calc_ema(prices, short_period) - calc_ema(prices, long_period)
    return calc_ema(macds, signal_period)


def calc_macd_oscillator(
    prices, short_period=12, long_period=26, signal_period=9
):
    macds = calc_ema(prices, short_period) - calc_ema(prices, long_period)
    macd_signals = calc_ema(macds, signal_period)
    return macds - macd_signals


def calc_gap(prices):
    gaps = list()
    for day, price in enumerate(prices):
        if day == 0:
            gaps.append(0)
        else:
            gaps.append(price - prices[day - 1])

    return np.array(gaps)


def calc_rsi(prices, window=14):
    gaps = calc_gap(prices)

    aus, ads = list(), list()
    for day, gap in enumerate(gaps):
        if day < window - 1:
            au, ad = 0, 0
        elif day == window - 1:
            au = np.sum([gap for gap in gaps[:window] if gap > 0]) / window
            ad = np.sum([-gap for gap in gaps[:window] if gap < 0]) / window
        elif gap > 0:
            au = ((window - 1) * aus[-1] + gap) / window
            ad = ((window - 1) * ads[-1] + 0) / window
        else:
            au = ((window - 1) * aus[-1] + 0) / window
            ad = ((window - 1) * ads[-1] - gap) / window

        aus.append(au)
        ads.append(ad)

    aus, ads = np.array(aus), np.array(ads)
    rsis = aus / (aus + ads) * 100
    rsis[:window] = 50.0

    return aus, ads, rsis


def calc_envelope(prices, window=20, spread=0.1, use_ema=False):
    mas = calc_ma(prices, window) if not use_ema else calc_ema(prices, window)
    return mas * (1 + spread), mas * (1 - spread)


def calc_mov_std(prices, window=20):
    mov_stds = list()
    for day, _ in enumerate(prices):
        if day < window - 1:
            mov_stds.append(0.0)
        else:
            mov_stds.append(np.std(prices[day - window + 1 : day + 1]))
    return np.array(mov_stds)


def calc_bollinger(prices, window=20, std_unit=2, use_ema=False):
    mov_stds = calc_mov_std(prices, window)
    mas = calc_ma(prices, window) if not use_ema else calc_ema(prices, window)
    return mas + std_unit * mov_stds, mas - std_unit * mov_stds


def calc_stochastic(prices, window=14):
    stochastics = list()
    for day, price in enumerate(prices):
        if day < window - 1:
            stochastics.append(50.0)
        else:
            max_price = max(prices[day - window + 1 : day + 1])
            min_price = min(prices[day - window + 1 : day + 1])
            stochastics.append(
                (price - min_price) / (max_price - min_price) * 100
            )
    return stochastics


def calc_stochastic_slow(prices, window=14, period_m=3, period_t=3):
    stochastics = calc_stochastic(prices, window)
    slow_ks = calc_ma(stochastics, period_m)
    slow_ds = calc_ma(slow_ks, period_t)
    return slow_ks, slow_ds

