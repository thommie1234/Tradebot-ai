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

    async def get_latest_news(self, symbol: str, hours_back: int = 4) -> List[Dict]:
        """
        Get latest news for a symbol.

        Returns:
            List of news articles with headline, summary, timestamp
        """
        try:
            # Use Alpaca News API (free with paper trading)
            url = f"https://data.alpaca.markets/v1beta1/news"
            params = {
                "symbols": symbol,
                "limit": 10,
                "start": (datetime.now() - timedelta(hours=hours_back)).isoformat() + "Z"
            }

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
                        })

                    logger.debug(f"Found {len(results)} news articles for {symbol}")
                    return results

        except Exception as e:
            logger.debug(f"Error fetching news for {symbol}: {e}")

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
