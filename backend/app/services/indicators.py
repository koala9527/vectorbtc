import pandas as pd
import numpy as np

def calculate_all(klines_data: list) -> dict:
    if not klines_data:
        return {}
        
    df = pd.DataFrame(klines_data)
    df = df.sort_values(by="open_time").reset_index(drop=True)
    
    close = df['close_price']
    
    # 1. MACD (12, 26, 9)
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
    # 2. RSI (14) using Wilder's RMA
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    # If avg_loss is 0, price only went up -> RSI is 100; if undefined, default to 50
    rsi = rsi.where(avg_loss != 0, 100.0)
    rsi = rsi.fillna(50.0)
    df['rsi_14'] = rsi
    
    # 3. Bollinger Bands (20, 2)
    df['sma_20'] = close.rolling(window=20, min_periods=1).mean()
    std_20 = close.rolling(window=20, min_periods=1).std().fillna(0)
    df['bb_upper'] = df['sma_20'] + (std_20 * 2)
    df['bb_lower'] = df['sma_20'] - (std_20 * 2)
    df['bb_middle'] = df['sma_20']
    
    # 4. EMAs
    df['ema_7'] = close.ewm(span=7, adjust=False).mean()
    df['ema_25'] = close.ewm(span=25, adjust=False).mean()
    
    # 5. SMA (99)
    df['sma_99'] = close.rolling(window=min(99, len(df)), min_periods=1).mean()
    
    latest = df.iloc[-1]
    
    def get_val(val):
        if pd.isna(val) or np.isinf(val):
            return None
        return round(float(val), 4)

    return {
        "macd": get_val(latest.get('macd')),
        "macd_signal": get_val(latest.get('macd_signal')),
        "macd_hist": get_val(latest.get('macd_hist')),
        "rsi_14": get_val(latest.get('rsi_14')),
        "bb_upper": get_val(latest.get('bb_upper')),
        "bb_middle": get_val(latest.get('bb_middle')),
        "bb_lower": get_val(latest.get('bb_lower')),
        "ema_7": get_val(latest.get('ema_7')),
        "ema_25": get_val(latest.get('ema_25')),
        "sma_99": get_val(latest.get('sma_99')),
    }
