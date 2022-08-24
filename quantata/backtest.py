import numpy as np
import pandas as pd


def calc_signal(
    ratios, buy_thresholds, sell_thresholds, buy_at_high_ratio=True
):
    signals = list()
    normalizer = np.std(ratios)

    for day, ratio in enumerate(ratios):
        if isinstance(buy_thresholds, (np.ndarray, pd.Series)):
            buy_th = buy_thresholds[day]
        else:
            buy_th = buy_thresholds
        if isinstance(sell_thresholds, (np.ndarray, pd.Series)):
            sell_th = sell_thresholds[day]
        else:
            sell_th = sell_thresholds

        signal = 0
        if buy_at_high_ratio:
            if ratio >= buy_th:
                signal = (ratio - buy_th) / normalizer
            elif ratio < sell_th:
                signal = -(sell_th - ratio) / normalizer

        else:
            if ratio <= buy_th:
                signal = (buy_th - ratio) / normalizer
            elif ratio > sell_th:
                signal = -(ratio - sell_th) / normalizer

        signals.append(signal)

    return np.array(signals)


def simulate(
    prices, signals, init_cap=0, trade_unit=0, init_pos=0, fee_rate=0.001
):
    amounts, volumes, fees, poses, caps = list(), list(), list(), list(), list()
    pos, cap = init_pos, init_cap

    if not trade_unit:
        trade_unit = np.ceil(init_cap / np.mean(prices)) if init_cap else 1

    for price, signal in zip(prices, signals):
        volume = abs(np.ceil(signal * trade_unit))
        amount = volume * price
        fee = np.ceil(amount * fee_rate)

        if signal > 0:
            if init_cap and cap < amount + fee:
                for unit in range(int(volume)):
                    volume = unit
                    amount = volume * price
                    fee = np.ceil(amount * fee_rate)
                    if cap < amount + fee:
                        volume = unit - 1
                        amount = volume * price
                        fee = np.ceil(amount * fee_rate)
                        break

            cap -= amount + fee
            pos += volume
            amounts.append(amount)
            volumes.append(volume)
            fees.append(fee)
            poses.append(pos)
            caps.append(cap)

        else:
            if pos < volume:
                volume = pos
                amount = volume * price
                fee = np.ceil(amount * fee_rate)

            cap += amount - fee
            pos -= volume
            amounts.append(-amount)
            volumes.append(-volume)
            fees.append(fee)
            poses.append(pos)
            caps.append(cap)

    return (
        np.array(amounts),
        np.array(volumes, np.int64),
        np.array(fees, np.int64),
        np.array(poses, np.int64),
        np.array(caps),
    )


def calc_asset(prices, poses, caps):
    return caps + poses * prices


def calc_return(caps):
    if caps[0]:
        return (caps[-1] - caps[0]) / caps[0]
    else:
        return 0.0
