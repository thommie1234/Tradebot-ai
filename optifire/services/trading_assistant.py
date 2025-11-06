"""
AI Trading Assistant - Answers questions about trades, positions, PnL, signals, etc.
"""
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from optifire.core.logger import logger
from optifire.core.db import Database
from optifire.exec.broker_alpaca import AlpacaBroker
from optifire.ai.openai_client import OpenAIClient


class TradingAssistant:
    """AI assistant that can answer questions about trading activity."""

    def __init__(self, db: Database, broker: AlpacaBroker, openai: OpenAIClient):
        self.db = db
        self.broker = broker
        self.openai = openai

    async def ask(self, question: str) -> str:
        """
        Answer a question about trading activity.

        Examples:
        - "Waarom is dit aandeel gekocht?"
        - "Hoeveel winst heb ik gemaakt vandaag?"
        - "Welke kansen heb je gezien?"
        - "Controleer AAPL voor mij"
        - "Wat zijn mijn beste trades?"
        """
        try:
            # Gather context about the portfolio
            context = await self._gather_context()

            # Build system prompt with context
            system_prompt = self._build_system_prompt(context)

            # Ask OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]

            response = await self.openai.chat_completion(
                messages=messages,
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=500
            )

            # Extract content from OpenAI response
            if "choices" in response and len(response["choices"]) > 0:
                answer = response["choices"][0]["message"]["content"]
            else:
                answer = "Sorry, ik kon geen antwoord genereren."

            return answer

        except Exception as e:
            logger.error(f"Trading assistant error: {e}", exc_info=True)
            return f"Sorry, er is een fout opgetreden: {str(e)}"

    async def _gather_context(self) -> Dict[str, Any]:
        """Gather all relevant trading context."""
        context = {
            "account": {},
            "positions": [],
            "recent_trades": [],
            "recent_signals": [],
            "performance": {}
        }

        try:
            # Account info
            account = await self.broker.get_account()
            context["account"] = {
                "equity": float(account.get("equity", 0)),
                "cash": float(account.get("cash", 0)),
                "buying_power": float(account.get("buying_power", 0)),
            }

            # Positions
            positions = await self.broker.get_positions()
            context["positions"] = [
                {
                    "symbol": pos.get("symbol"),
                    "qty": float(pos.get("qty", 0)),
                    "avg_entry": float(pos.get("avg_entry_price", 0)),
                    "current_price": float(pos.get("current_price", 0)),
                    "unrealized_pnl": float(pos.get("unrealized_pl", 0)),
                    "unrealized_pnl_pct": float(pos.get("unrealized_plpc", 0)) * 100,
                }
                for pos in positions
            ]

        except Exception as e:
            logger.warning(f"Failed to get account/positions from broker: {e}")

        try:
            # Recent trades from database
            async with self.db.connection() as conn:
                cursor = await conn.execute(
                    """
                    SELECT symbol, side, qty, status, submitted_at, filled_at, metadata
                    FROM orders
                    WHERE submitted_at IS NOT NULL AND submitted_at > datetime('now', '-7 days')
                    ORDER BY submitted_at DESC
                    LIMIT 20
                    """
                )
                rows = await cursor.fetchall()

                for row in rows:
                    metadata = json.loads(row[6]) if row[6] else {}
                    context["recent_trades"].append({
                        "symbol": row[0],
                        "side": row[1],
                        "qty": row[2],
                        "status": row[3],
                        "submitted_at": row[4],
                        "filled_at": row[5],
                        "reason": metadata.get("reason", "Unknown"),
                        "signal_type": metadata.get("signal_type", "manual"),
                    })

                # Recent signals from auto-trader
                cursor = await conn.execute(
                    """
                    SELECT symbol, signal_type, confidence, metadata, created_at
                    FROM signals
                    WHERE created_at > datetime('now', '-7 days')
                    ORDER BY created_at DESC
                    LIMIT 20
                    """
                )
                rows = await cursor.fetchall()

                for row in rows:
                    metadata = json.loads(row[3]) if row[3] else {}
                    context["recent_signals"].append({
                        "symbol": row[0],
                        "signal_type": row[1],
                        "confidence": row[2] if row[2] else 0.5,
                        "reason": metadata.get("reason", "No reason provided"),
                        "timestamp": row[4],
                    })

        except Exception as e:
            logger.warning(f"Failed to get trades/signals from database: {e}")

        # Calculate performance
        context["performance"] = self._calculate_performance(context)

        return context

    def _calculate_performance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics."""
        perf = {
            "total_pnl": 0.0,
            "win_rate": 0.0,
            "best_trade": None,
            "worst_trade": None,
        }

        # Sum unrealized PnL
        for pos in context["positions"]:
            perf["total_pnl"] += pos["unrealized_pnl"]

        # Calculate win rate from filled trades
        filled_trades = [t for t in context["recent_trades"] if t["status"] == "filled"]
        if filled_trades:
            # We don't have realized PnL in the orders table, so we can't calculate win rate accurately
            # This would require matching buy/sell pairs
            pass

        # Find best/worst positions
        if context["positions"]:
            best = max(context["positions"], key=lambda p: p["unrealized_pnl"])
            worst = min(context["positions"], key=lambda p: p["unrealized_pnl"])
            perf["best_trade"] = f"{best['symbol']} (+${best['unrealized_pnl']:.2f})"
            perf["worst_trade"] = f"{worst['symbol']} (${worst['unrealized_pnl']:.2f})"

        return perf

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with trading context."""

        # Format context into readable text
        account_text = f"""
Account Status:
- Equity: ${context['account'].get('equity', 0):,.2f}
- Cash: ${context['account'].get('cash', 0):,.2f}
- Buying Power: ${context['account'].get('buying_power', 0):,.2f}
"""

        positions_text = "Current Positions:\n"
        if context["positions"]:
            for pos in context["positions"]:
                positions_text += f"- {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry']:.2f}, Current: ${pos['current_price']:.2f}, P&L: ${pos['unrealized_pnl']:.2f} ({pos['unrealized_pnl_pct']:.1f}%)\n"
        else:
            positions_text += "- No open positions\n"

        trades_text = "Recent Trades (Last 7 days):\n"
        if context["recent_trades"]:
            for trade in context["recent_trades"][:10]:
                trades_text += f"- {trade['submitted_at']}: {trade['side'].upper()} {trade['qty']} {trade['symbol']} ({trade['status']}) - Reason: {trade['reason']}\n"
        else:
            trades_text += "- No recent trades\n"

        signals_text = "Recent Signals (Last 7 days):\n"
        if context["recent_signals"]:
            for signal in context["recent_signals"][:10]:
                signals_text += f"- {signal['timestamp']}: {signal['symbol']} ({signal['signal_type']}) - {signal['reason']} (Confidence: {signal['confidence']:.0%})\n"
        else:
            signals_text += "- No recent signals\n"

        performance_text = f"""
Performance Summary:
- Total Unrealized P&L: ${context['performance']['total_pnl']:.2f}
- Best Position: {context['performance'].get('best_trade', 'N/A')}
- Worst Position: {context['performance'].get('worst_trade', 'N/A')}
"""

        system_prompt = f"""Je bent een AI trading assistent voor het OptiFIRE trading systeem. Je helpt de gebruiker door vragen te beantwoorden over:
- Waarom bepaalde aandelen gekocht/verkocht zijn
- Winst en verlies (P&L)
- Welke handelskansen het systeem heeft gedetecteerd
- Portfolio analyse en advies
- Status van specifieke aandelen

Je hebt toegang tot de volgende real-time data:

{account_text}

{positions_text}

{trades_text}

{signals_text}

{performance_text}

Geef altijd concrete, nuttige antwoorden gebaseerd op de data. Als je naar een specifiek aandeel wordt gevraagd, geef dan details over:
1. Of we het in portfolio hebben (positie)
2. Recente trades
3. Recente signalen/kansen
4. Huidige performance

Antwoord in het Nederlands tenzij de gebruiker Engels gebruikt. Wees kort, duidelijk en actionable."""

        return system_prompt
