"""
Earnings calendar service.
Fetches upcoming earnings dates for stocks.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
import yfinance as yf

from optifire.core.logger import logger


class EarningsCalendar:
    """
    Earnings calendar service.

    Uses yfinance library to get earnings dates.
    """

    def __init__(self):
        self.cache: Dict[str, tuple] = {}  # {symbol: (days_until, timestamp)}
        self.cache_ttl = 3600 * 12  # 12 hours

    async def get_upcoming_earnings(
        self,
        symbols: Optional[List[str]] = None,
        days_ahead: int = 14
    ) -> Dict[str, int]:
        """
        Get upcoming earnings for symbols.

        Returns:
            Dict[symbol, days_until_earnings]
        """
        if symbols is None:
            symbols = self._get_default_watchlist()

        results = {}

        for i, symbol in enumerate(symbols):
            try:
                days_until = await self.get_days_until_earnings(symbol)
                if days_until is not None and 0 <= days_until <= days_ahead:
                    results[symbol] = days_until
                    logger.info(f"📅 {symbol} earnings in {days_until} days")

                # Rate limiting: sleep between requests (avoid API throttling)
                # Sleep 0.5s between requests (max 2 requests/sec)
                if i < len(symbols) - 1:  # Don't sleep after last symbol
                    await asyncio.sleep(0.5)

            except Exception as e:
                logger.debug(f"Could not get earnings for {symbol}: {e}")

        return results

    async def get_days_until_earnings(self, symbol: str, max_retries: int = 3) -> Optional[int]:
        """
        Get days until next earnings for a symbol.

        Uses yfinance library with caching, rate limiting, and retry logic.
        """
        # Check cache first
        now = datetime.now()
        if symbol in self.cache:
            days_until, cache_time = self.cache[symbol]
            if (now - cache_time).total_seconds() < self.cache_ttl:
                logger.debug(f"{symbol} earnings from cache: {days_until} days")
                return days_until

        # Retry with exponential backoff
        for attempt in range(max_retries):
            try:
                # Fetch from yfinance (run in thread pool to avoid blocking)
                loop = asyncio.get_event_loop()
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                calendar = await loop.run_in_executor(None, lambda: ticker.calendar)

                if calendar is None or (isinstance(calendar, dict) and not calendar):
                    logger.debug(f"No earnings calendar data for {symbol}")
                    return None

                # Parse earnings date
                earnings_date = None
                if isinstance(calendar, dict):
                    # Format: {'Earnings Date': [datetime.date(2025, 11, 4)], ...}
                    earnings_dates = calendar.get('Earnings Date', [])
                    if earnings_dates and len(earnings_dates) > 0:
                        earnings_date = earnings_dates[0]

                if earnings_date:
                    # Calculate days until
                    if hasattr(earnings_date, 'date'):
                        earnings_date = earnings_date.date()

                    today = datetime.now().date()
                    days_until = (earnings_date - today).days

                    # Cache the result
                    self.cache[symbol] = (days_until, now)

                    logger.debug(f"{symbol} earnings in {days_until} days ({earnings_date})")
                    return days_until

                return None

            except Exception as e:
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    logger.debug(f"Error fetching {symbol} (attempt {attempt+1}/{max_retries}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.debug(f"Error fetching earnings for {symbol} after {max_retries} attempts: {e}")
                    return None

        return None

    def _get_default_watchlist(self) -> List[str]:
        """Get default watchlist for earnings."""
        return [
            # Tech mega-caps
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
            # Other large caps
            "NFLX", "AMD", "CRM", "ADBE", "INTC", "CSCO", "ORCL",
            # High beta / meme stocks
            "GME", "AMC", "PLTR", "COIN", "SHOP", "SQ", "SNAP",
        ]


# Example usage
async def main():
    calendar = EarningsCalendar()
    upcoming = await calendar.get_upcoming_earnings(days_ahead=7)

    print("Upcoming earnings (next 7 days):")
    for symbol, days in sorted(upcoming.items(), key=lambda x: x[1]):
        print(f"  {symbol}: {days} days")


if __name__ == "__main__":
    asyncio.run(main())
