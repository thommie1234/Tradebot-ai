"""
Feature engineering utilities.
"""
import numpy as np
import pandas as pd
from typing import Optional

from optifire.core.logger import logger


class FeatureEngineer:
    """Feature engineering toolkit."""
    
    @staticmethod
    def calculate_returns(prices: pd.Series, periods: int = 1) -> pd.Series:
        """Calculate returns."""
        return prices.pct_change(periods)
    
    @staticmethod
    def calculate_log_returns(prices: pd.Series, periods: int = 1) -> pd.Series:
        """Calculate log returns."""
        return np.log(prices / prices.shift(periods))
    
    @staticmethod
    def calculate_volatility(
        returns: pd.Series,
        window: int = 20,
        annualize: bool = True,
    ) -> pd.Series:
        """Calculate rolling volatility."""
        vol = returns.rolling(window).std()
        if annualize:
            vol *= np.sqrt(252)
        return vol
    
    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14,
    ) -> pd.Series:
        """Calculate Average True Range."""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        return atr
    
    @staticmethod
    def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI."""
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(
        close: pd.Series,
        period: int = 20,
        std_dev: float = 2.0,
    ) -> tuple:
        """Calculate Bollinger Bands."""
        sma = close.rolling(period).mean()
        std = close.rolling(period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower
    
    @staticmethod
    def calculate_ema(close: pd.Series, period: int) -> pd.Series:
        """Calculate EMA."""
        return close.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_macd(
        close: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> tuple:
        """Calculate MACD."""
        ema_fast = FeatureEngineer.calculate_ema(close, fast)
        ema_slow = FeatureEngineer.calculate_ema(close, slow)
        macd = ema_fast - ema_slow
        signal_line = FeatureEngineer.calculate_ema(macd, signal)
        histogram = macd - signal_line
        return macd, signal_line, histogram
