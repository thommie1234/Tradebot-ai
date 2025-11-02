"""
Earnings calendar service.
Fetches upcoming earnings dates for stocks.
"""
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio

from optifire.core.logger import logger


class EarningsCalendar:
    """
    Earnings calendar service.

    Uses free APIs to get earnings dates.
    """

    def __init__(self):
        self.cache: Dict[str, datetime] = {}
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

        for symbol in symbols:
            try:
                days_until = await self.get_days_until_earnings(symbol)
                if days_until is not None and 0 <= days_until <= days_ahead:
                    results[symbol] = days_until
            except Exception as e:
                logger.debug(f"Could not get earnings for {symbol}: {e}")

        return results

    async def get_days_until_earnings(self, symbol: str) -> Optional[int]:
        """
        Get days until next earnings for a symbol.

        Uses Yahoo Finance API (free).
        """
        try:
            # Use Yahoo Finance API (unofficial but free)
            url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
            params = {
                "modules": "calendarEvents"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            # Extract earnings date
            calendar = data.get("quoteSummary", {}).get("result", [{}])[0]
            events = calendar.get("calendarEvents", {})
            earnings_date = events.get("earnings", {}).get("earningsDate")

            if earnings_date and len(earnings_date) > 0:
                # Parse earnings date (Unix timestamp)
                earnings_ts = earnings_date[0].get("raw")
                if earnings_ts:
                    earnings_dt = datetime.fromtimestamp(earnings_ts)
                    now = datetime.now()
                    days_until = (earnings_dt - now).days

                    logger.debug(f"{symbol} earnings in {days_until} days ({earnings_dt.date()})")
                    return days_until

            return None

        except Exception as e:
            logger.debug(f"Error fetching earnings for {symbol}: {e}")
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
