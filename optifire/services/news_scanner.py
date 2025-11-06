"""
News scanner service.
Fetches and analyzes news for trading signals.
"""
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio

from optifire.core.logger import logger
from optifire.ai.openai_client import OpenAIClient


class NewsScanner:
    """
    News scanner for trading signals.

    Fetches news from multiple sources and analyzes with AI.
    """

    def __init__(self):
        self.openai = OpenAIClient()
        self.cache: Dict[str, List[Dict]] = {}

    async def get_latest_news(self, symbol: str = None, hours_back: int = 4) -> List[Dict]:
        """
        Get latest news for a symbol, or market-wide news if symbol is None.

        Args:
            symbol: Stock symbol (e.g., "AAPL"), or None for market-wide news
            hours_back: How many hours back to search

        Returns:
            List of news articles with headline, summary, timestamp
        """
        try:
            # Use Alpaca News API (free with paper trading)
            url = f"https://data.alpaca.markets/v1beta1/news"
            params = {
                "limit": 20 if symbol is None else 10,  # More articles for market-wide
                "start": (datetime.now() - timedelta(hours=hours_back)).isoformat() + "Z"
            }

            # Only add symbols param if symbol is provided
            if symbol:
                params["symbols"] = symbol

            headers = {
                "APCA-API-KEY-ID": self._get_alpaca_key(),
                "APCA-API-SECRET-KEY": self._get_alpaca_secret(),
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("news", [])

                    results = []
                    for article in articles:
                        results.append({
                            "headline": article.get("headline", ""),
                            "summary": article.get("summary", ""),
                            "url": article.get("url", ""),
                            "timestamp": article.get("created_at", ""),
                            "source": article.get("source", ""),
                            "symbols": article.get("symbols", []),  # Track related symbols
                        })

                    scope = "market-wide" if symbol is None else symbol
                    logger.debug(f"Found {len(results)} news articles for {scope}")
                    return results

        except Exception as e:
            scope = "market-wide" if symbol is None else symbol
            logger.debug(f"Error fetching news for {scope}: {e}")

        # Fallback: use web scraping or return empty
        return []

    async def analyze_news_sentiment(
        self,
        symbol: str,
        articles: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Analyze news sentiment for trading signal.

        Returns:
            {
                "action": "BUY" | "SHORT" | "SKIP",
                "confidence": 0.0 - 1.0,
                "reason": "Explanation",
                "key_headline": "Most important headline"
            }
        """
        if articles is None:
            articles = await self.get_latest_news(symbol)

        if not articles:
            return {
                "action": "SKIP",
                "confidence": 0.0,
                "reason": "No recent news",
                "key_headline": None
            }

        # Combine headlines
        headlines_text = "\n".join([
            f"- {a['headline']}"
            for a in articles[:5]
        ])

        # Analyze with OpenAI
        prompt = f"""Analyze these news headlines for {symbol} and determine if there's a strong trading opportunity.

Recent headlines:
{headlines_text}

Instructions:
1. Look for major catalysts:
   - Partnership announcements (e.g., "NVIDIA partners with OpenAI")
   - Product launches
   - Earnings beats/misses
   - FDA approvals/rejections
   - Major contracts won/lost
   - Leadership changes
   - Regulatory issues/lawsuits

2. Determine:
   - BUY: Strong positive catalyst (high confidence only) - go LONG
   - SHORT: Strong negative catalyst (high confidence only) - bet against the stock
   - SKIP: No strong catalyst or unclear sentiment

3. Respond in this exact format:
ACTION: [BUY|SHORT|SKIP]
CONFIDENCE: [0.0-1.0]
REASON: [One sentence explanation]
KEY_HEADLINE: [The most important headline]

Be conservative - only signal BUY/SHORT if confidence > 0.7
"""

        try:
            result = await self.openai.analyze_text(
                prompt,
                purpose=f"News Analysis: {symbol}"
            )

            # Parse response
            action = "SKIP"
            confidence = 0.0
            reason = "No clear signal"
            key_headline = articles[0]["headline"] if articles else None

            for line in result.split("\n"):
                if line.startswith("ACTION:"):
                    action = line.split(":")[1].strip().upper()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.split(":")[1].strip())
                    except:
                        confidence = 0.0
                elif line.startswith("REASON:"):
                    reason = line.split(":", 1)[1].strip()
                elif line.startswith("KEY_HEADLINE:"):
                    key_headline = line.split(":", 1)[1].strip()

            return {
                "action": action,
                "confidence": confidence,
                "reason": reason,
                "key_headline": key_headline
            }

        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            return {
                "action": "SKIP",
                "confidence": 0.0,
                "reason": f"Analysis error: {str(e)}",
                "key_headline": None
            }

    def _get_alpaca_key(self) -> str:
        """Get Alpaca API key."""
        import os
        return os.getenv("ALPACA_API_KEY", "")

    def _get_alpaca_secret(self) -> str:
        """Get Alpaca API secret."""
        import os
        return os.getenv("ALPACA_API_SECRET", "")

    async def analyze_macro_news(self) -> Dict:
        """
        Analyze market-wide and macro news for systemic signals.

        Looks for:
        - Fed policy changes (rate hikes, cuts, QE/QT)
        - Inflation data (CPI, PPI)
        - Geopolitical events (wars, trade disputes)
        - Banking crises, credit events
        - Tech sector-wide events
        - Market-wide selloffs or rallies

        Returns:
            {
                "market_regime": "RISK_ON" | "RISK_OFF" | "NEUTRAL",
                "confidence": 0.0 - 1.0,
                "action": "DEFENSIVE" | "AGGRESSIVE" | "NEUTRAL",
                "reason": "Explanation",
                "affected_sectors": ["TECH", "FINANCE", ...]
            }
        """
        try:
            # Get market-wide news (no symbol filter)
            articles = await self.get_latest_news(symbol=None, hours_back=6)

            if not articles:
                return {
                    "market_regime": "NEUTRAL",
                    "confidence": 0.0,
                    "action": "NEUTRAL",
                    "reason": "No significant market-wide news",
                    "affected_sectors": []
                }

            # Combine headlines
            headlines_text = "\n".join([
                f"- {a['headline']}"
                for a in articles[:15]
            ])

            # Analyze with OpenAI
            prompt = f"""Analyze these market-wide headlines for SYSTEMIC trading signals.

Recent market headlines:
{headlines_text}

Look for MACRO catalysts:
1. Federal Reserve policy:
   - Rate hikes/cuts
   - QE/QT (quantitative easing/tightening)
   - Powell speeches, FOMC meetings

2. Economic data:
   - CPI/PPI (inflation)
   - Jobs data (unemployment, payrolls)
   - GDP, consumer sentiment

3. Geopolitical events:
   - Wars, conflicts
   - Trade disputes (tariffs, sanctions)
   - Political instability

4. Financial system stress:
   - Bank failures
   - Credit spreads widening
   - Liquidity crises

5. Sector-wide events:
   - Tech sector selloff
   - Energy crisis
   - Regulatory changes

Determine the MARKET REGIME:
- RISK_ON: Markets rallying, optimism, "buy the dip" mentality
- RISK_OFF: Markets selling off, fear, flight to safety (bonds, gold, cash)
- NEUTRAL: No clear systemic signal

Recommended ACTION:
- DEFENSIVE: Reduce exposure, hedge, move to safe havens (TLT, GLD)
- AGGRESSIVE: Increase exposure, buy high-beta stocks
- NEUTRAL: No change needed

Respond in this EXACT format:
MARKET_REGIME: [RISK_ON|RISK_OFF|NEUTRAL]
CONFIDENCE: [0.0-1.0]
ACTION: [DEFENSIVE|AGGRESSIVE|NEUTRAL]
REASON: [One clear sentence]
AFFECTED_SECTORS: [Comma-separated: TECH,FINANCE,ENERGY,HEALTHCARE,etc or BROAD_MARKET]
"""

            result = await self.openai.analyze_text(
                prompt,
                purpose="Macro Market Analysis"
            )

            # Parse response
            market_regime = "NEUTRAL"
            confidence = 0.0
            action = "NEUTRAL"
            reason = "No clear systemic signal"
            affected_sectors = []

            for line in result.split("\n"):
                if line.startswith("MARKET_REGIME:"):
                    market_regime = line.split(":")[1].strip().upper()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.split(":")[1].strip())
                    except:
                        confidence = 0.0
                elif line.startswith("ACTION:"):
                    action = line.split(":")[1].strip().upper()
                elif line.startswith("REASON:"):
                    reason = line.split(":", 1)[1].strip()
                elif line.startswith("AFFECTED_SECTORS:"):
                    sectors_str = line.split(":", 1)[1].strip()
                    affected_sectors = [s.strip() for s in sectors_str.split(",")]

            logger.info(f"🌍 Macro analysis: {market_regime} ({confidence:.0%}) - {action}")
            logger.info(f"   Reason: {reason}")

            return {
                "market_regime": market_regime,
                "confidence": confidence,
                "action": action,
                "reason": reason,
                "affected_sectors": affected_sectors
            }

        except Exception as e:
            logger.error(f"Error analyzing macro news: {e}")
            return {
                "market_regime": "NEUTRAL",
                "confidence": 0.0,
                "action": "NEUTRAL",
                "reason": f"Analysis error: {str(e)}",
                "affected_sectors": []
            }


# Example usage
async def main():
    scanner = NewsScanner()

    # Test with NVDA
    print("Testing news scanner for NVDA...")
    analysis = await scanner.analyze_news_sentiment("NVDA")

    print(f"\nAction: {analysis['action']}")
    print(f"Confidence: {analysis['confidence']:.0%}")
    print(f"Reason: {analysis['reason']}")
    print(f"Key headline: {analysis['key_headline']}")


if __name__ == "__main__":
    asyncio.run(main())
