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

