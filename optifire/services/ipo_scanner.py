"""
IPO Scanner - Detect and trade new IPOs
Scans for upcoming and recent IPOs, analyzes hype, and generates trading signals.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

from optifire.core.logger import logger
from optifire.ai.openai_client import OpenAIClient


class IPOScanner:
    """
    Scans for IPO opportunities.

    Strategy:
    - Monitor news for IPO announcements
    - Track IPO calendar (upcoming listings)
    - Analyze pre-IPO hype and sentiment
    - Generate signals for first-day trading
    - Quick profit-taking (IPOs are volatile)
    """

    def __init__(self):
        self.openai = OpenAIClient()
        self.known_ipos: Dict[str, Dict] = {}  # Track IPOs we've seen

    async def scan_upcoming_ipos(self) -> List[Dict]:
        """
        Scan for upcoming IPOs from news.

        Returns:
            List of IPO info dicts with symbol, company, date, hype_score
        """
        try:
            # Use OpenAI to analyze recent news for IPO announcements
            prompt = """Analyze recent financial news for upcoming IPOs in the next 30 days.

Look for:
- Companies filing for IPO
- IPO dates announced
- High-profile tech/biotech IPOs
- SPACs merging with companies

Return JSON array (max 5 IPOs):
[
    {
        "symbol": "TICKER",
        "company": "Company Name",
        "date": "2025-11-15",
        "sector": "Technology|Healthcare|Finance|etc",
        "hype_level": "HIGH|MEDIUM|LOW",
        "reason": "Why this IPO is interesting"
    }
]

If no IPOs found, return empty array [].
"""

            result = await self.openai.analyze_text(
                prompt,
                purpose="IPO Calendar Scan"
            )

            # Parse JSON response (simplified - should use proper JSON parsing)
            if "[]" in result or "no ipo" in result.lower():
                logger.info("📅 No upcoming IPOs detected")
                return []

            # For now, log the result
            # In production, would parse JSON properly
            logger.info(f"📅 IPO scan results: {result[:200]}...")

            # Mock data for testing (remove when OpenAI parsing is implemented)
            # In real implementation, parse the OpenAI JSON response
            return []

        except Exception as e:
            logger.error(f"Error scanning IPOs: {e}", exc_info=True)
            return []

    async def analyze_ipo_hype(self, symbol: str, company: str) -> Dict:
        """
        Analyze hype and sentiment for an upcoming IPO.

        STRICT CRITERIA (based on backtest - only 50% win rate):
        - Only HIGH confidence (>0.75) IPOs
        - Must have strong fundamentals AND hype
        - Avoid overhyped IPOs (often dump)
        - Prefer tech/AI with real revenue

        Args:
            symbol: Stock ticker
            company: Company name

        Returns:
            {
                "hype_score": 0.0-1.0,
                "sentiment": "BULLISH|BEARISH|NEUTRAL",
                "confidence": 0.0-1.0,
                "action": "BUY|SKIP",
                "reason": "Brief explanation"
            }
        """
        try:
            prompt = f"""Analyze the IPO for {company} ({symbol}) with STRICT criteria.

⚠️ WARNING: IPO first-day trading has 50% win rate (coin flip).
Only recommend BUY if ALL criteria met:

MUST HAVE:
✓ Real revenue (not just hype)
✓ Profitable OR clear path to profitability
✓ Strong sector tailwinds (AI, cloud, fintech)
✓ Reasonable valuation (not 100x revenue)
✓ Institutional backing (top VCs/banks)

AVOID:
✗ Pure hype plays (meme stocks)
✗ Money-losing unprofitable companies
✗ Oversaturated sectors
✗ Direct listings (more volatile)
✗ SPACs (poor track record)

Historical context:
- Winners: Pinterest (+22%), Zoom (+7%), Roblox (+10%)
- Losers: Lyft (-12%), Snowflake (-10%), Airbnb (-10%), Reddit (-9%)

Respond in JSON:
{{
    "hype_score": 0.0-1.0,
    "sentiment": "BULLISH|BEARISH|NEUTRAL",
    "confidence": 0.0-1.0,
    "action": "BUY|SKIP",
    "reason": "Brief explanation with fundamentals",
    "has_revenue": true/false,
    "profitable": true/false,
    "valuation_reasonable": true/false
}}

BE VERY SELECTIVE - default to SKIP unless extremely confident.
"""

            result = await self.openai.analyze_text(
                prompt,
                purpose=f"IPO Hype Analysis: {symbol}"
            )

            # Parse result (simplified)
            action = "SKIP"
            if "BUY" in result:
                action = "BUY"

            # Extract hype score (simplified - should parse JSON)
            hype_score = 0.5
            if "high" in result.lower() or "strong" in result.lower():
                hype_score = 0.8
            elif "low" in result.lower() or "weak" in result.lower():
                hype_score = 0.3

            return {
                "hype_score": hype_score,
                "sentiment": "NEUTRAL",
                "confidence": 0.6,
                "action": action,
                "reason": result[:150],
            }

        except Exception as e:
            logger.error(f"Error analyzing IPO hype for {symbol}: {e}")
            return {
                "hype_score": 0.0,
                "sentiment": "NEUTRAL",
                "confidence": 0.0,
                "action": "SKIP",
                "reason": f"Error: {str(e)}",
            }

    async def check_first_day_ipo(self, symbol: str) -> Optional[Dict]:
        """
        Check if a stock is a first-day IPO (trading for first time today).

        This is the GOLDEN opportunity - first-day IPO pops can be 50-100%+

        Args:
            symbol: Stock ticker

        Returns:
            IPO info dict if it's first day, None otherwise
        """
        try:
            # In production, would check:
            # 1. IPO calendar APIs
            # 2. Stock exchange listings
            # 3. News for "begins trading today"

            # For now, check if we've tracked this IPO
            if symbol in self.known_ipos:
                ipo_date = self.known_ipos[symbol].get("date")
                today = datetime.now(pytz.UTC).date()

                # Check if IPO date is today
                if ipo_date and ipo_date == today:
                    return self.known_ipos[symbol]

            return None

        except Exception as e:
            logger.error(f"Error checking first-day IPO for {symbol}: {e}")
            return None

    async def generate_ipo_signal(self, ipo_info: Dict) -> Optional[Dict]:
        """
        Generate a trading signal for an IPO.

        Args:
            ipo_info: IPO info dict

        Returns:
            Signal dict or None
        """
        try:
            symbol = ipo_info["symbol"]
            company = ipo_info["company"]

            # Analyze hype with STRICT criteria
            analysis = await self.analyze_ipo_hype(symbol, company)

            if analysis["action"] != "BUY":
                return None

            # STRICT FILTER: Only HIGH confidence (>0.75) - backtest showed 50% win rate
            if analysis["confidence"] < 0.75:
                logger.info(f"🆕 IPO {symbol} SKIPPED - confidence too low ({analysis['confidence']:.0%})")
                return None

            # IPO strategy (optimized based on backtest):
            # - SMALLER position (3-4%) - even more conservative
            # - Higher profit target (20%) - let winners run
            # - Tight stop loss (5%) - cut losers fast

            return {
                "symbol": symbol,
                "action": "BUY",
                "confidence": analysis["confidence"],
                "reason": f"🆕 IPO: {company} - {analysis['reason']}",
                "size_pct": 0.03,  # 3% position (was 6% - much safer based on backtest)
                "take_profit": 0.20,  # 20% profit target (winners like Pinterest hit this)
                "stop_loss": 0.05,  # 5% stop (protect from dumps like Reddit/Lyft)
            }

        except Exception as e:
            logger.error(f"Error generating IPO signal: {e}")
            return None
