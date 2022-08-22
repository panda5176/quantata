import numpy as np
import pandas as pd


def calc_signal(
    ratios,
    buy_thresholds,
    sell_thresholds,
    buy_weight=1,
    sell_weight=10,
    trade_unit=10,
    buy_at_high_ratio=True,
):
    signals = list()
    buy_intensity = buy_weight * trade_unit / np.std(ratios)
    sell_intensity = sell_weight * trade_unit / np.std(ratios)

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
                signal = np.floor((ratio - buy_th) * buy_intensity)
            elif ratio < sell_th:
                signal = -np.floor((sell_th - ratio) * sell_intensity)

        else:
            if ratio <= buy_th:
                signal = np.floor((buy_th - ratio) * buy_intensity)
            elif ratio > sell_th:
                signal = -np.floor((ratio - sell_th) * sell_intensity)

        signals.append(signal)

    return np.array(signals, np.int64)


def simulate(prices, signals, init_cap=0, init_pos=0, fee_rate=0.001):
    amounts, volumes, fees, poses, caps = list(), list(), list(), list(), list()
    pos, cap = init_pos, init_cap

    for price, signal in zip(prices, signals):
        volume = abs(signal)
        amount = volume * price
        fee = np.ceil(amount * fee_rate)

        if signal > 0:
            if init_cap or cap >= amount + fee:
                cap -= amount + fee
                pos += volume
                amounts.append(amount)
                volumes.append(volume)
                fees.append(fee)
                poses.append(pos)
                caps.append(cap)
                continue

        elif pos >= volume:
            if cap >= fee or amount >= fee or cap + amount >= fee:
                cap += amount - fee
                pos -= volume
                amounts.append(-amount)
                volumes.append(-volume)
                fees.append(fee)
                poses.append(pos)
                caps.append(cap)
                continue

        else:
            volume = pos
            amount = volume * price
            fee = np.ceil(amount * fee_rate)

            if cap >= fee or amount >= fee or cap + amount >= fee:
                cap += amount - fee
                pos -= volume
                amounts.append(-amount)
                volumes.append(-volume)
                fees.append(fee)
                poses.append(pos)
                caps.append(cap)
                continue

        amounts.append(0)
        volumes.append(0)
        fees.append(0)
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
