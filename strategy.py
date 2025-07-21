import pandas as pd

class FractalShiftStrategy:
    def __init__(self, rr_ratio=2.0):
        self.rr_ratio = rr_ratio

    def backtest(self, df: pd.DataFrame, lot_size: float = 0.13):
        df = df.copy()
        df['Fractal_High'] = df['High'].shift(2).rolling(window=5).max()
        df['Fractal_Low'] = df['Low'].shift(2).rolling(window=5).min()
        df.dropna(inplace=True)

        trades = []
        for i in range(1, len(df)):
            candle = df.iloc[i]
            prev = df.iloc[i - 1]

            # Sample condition: Bullish breakout
            if candle['Close'] > prev['Fractal_High']:
                entry = candle['Close']
                sl = entry - (entry - prev['Fractal_Low'])
                tp = entry + self.rr_ratio * (entry - sl)
                trades.append({
                    'Direction': 'BUY',
                    'Entry': entry,
                    'SL': sl,
                    'TP': tp,
                    'Lot': lot_size,
                    'Time': candle['Time']
                })

            # Sample condition: Bearish breakdown
            elif candle['Close'] < prev['Fractal_Low']:
                entry = candle['Close']
                sl = entry + (prev['Fractal_High'] - entry)
                tp = entry - self.rr_ratio * (sl - entry)
                trades.append({
                    'Direction': 'SELL',
                    'Entry': entry,
                    'SL': sl,
                    'TP': tp,
                    'Lot': lot_size,
                    'Time': candle['Time']
                })

        return trades
