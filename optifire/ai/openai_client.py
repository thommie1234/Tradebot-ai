"""
OpenAI client for AI/ML features.
"""
import os
from typing import List, Optional, Dict, Any
import httpx
from datetime import datetime
import json
import sqlite3

from optifire.core.logger import logger
from optifire.core.errors import ExecutionError


class OpenAIClient:
    """
    OpenAI API client for sentiment analysis, embeddings, and chat.
    """

    def __init__(self, db_path: str = "/root/optifire/data/optifire.db"):
        """Initialize OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.db_path = db_path

        if not self.api_key:
            logger.warning("OpenAI API key not found in environment")

        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key or ''}",
            "Content-Type": "application/json",
        }

        # Initialize conversation logging table
        self._init_conversation_table()

    def _init_conversation_table(self):
        """Create table for logging OpenAI conversations."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS openai_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model TEXT NOT NULL,
                    purpose TEXT,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    tokens_used INTEGER,
                    cost_usd REAL,
                    temperature REAL,
                    max_tokens INTEGER
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp
                ON openai_conversations(timestamp DESC)
            """)
            conn.commit()
            conn.close()
            logger.debug("OpenAI conversation table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize conversation table: {e}")

    def _log_conversation(
        self,
        model: str,
        purpose: str,
        prompt: str,
        response: str,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        temperature: float = 0.0,
        max_tokens: int = 0
    ):
        """Log conversation to database and file."""
        try:
            # Log to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO openai_conversations
                (timestamp, model, purpose, prompt, response, tokens_used, cost_usd, temperature, max_tokens)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                model,
                purpose,
                prompt,
                response,
                tokens_used,
                cost_usd,
                temperature,
                max_tokens
            ))
            conn.commit()
            conn.close()

            # Also log to file for easy viewing
            log_dir = "/root/optifire/data/openai_logs"
            os.makedirs(log_dir, exist_ok=True)
            log_file = f"{log_dir}/conversations_{datetime.now().strftime('%Y-%m-%d')}.log"

            with open(log_file, "a") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
                f.write(f"MODEL: {model}\n")
                f.write(f"PURPOSE: {purpose}\n")
                f.write(f"TEMPERATURE: {temperature}\n")
                f.write(f"MAX_TOKENS: {max_tokens}\n")
                f.write(f"TOKENS_USED: {tokens_used}\n")
                f.write(f"COST: ${cost_usd:.4f}\n")
                f.write(f"\n--- PROMPT ---\n{prompt}\n")
                f.write(f"\n--- RESPONSE ---\n{response}\n")
                f.write(f"{'='*80}\n")

            logger.debug(f"Logged OpenAI conversation: {purpose}")

        except Exception as e:
            logger.error(f"Failed to log conversation: {e}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Dict[str, Any]:
        """
        Get chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (gpt-4o-mini is cost effective)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Chat completion response
        """
        if not self.api_key:
            raise ExecutionError("OpenAI API key not configured")

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def analyze_sentiment(
        self,
        text: str,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text for trading signals.

        Args:
            text: Text to analyze (news, earnings call, etc.)
            context: Optional context (e.g., "earnings call for AAPL")

        Returns:
            {
                "sentiment": "bullish" | "bearish" | "neutral",
                "score": float (-1 to 1),
                "confidence": float (0 to 1),
                "reasoning": str
            }
        """
        prompt = f"Analyze the following text for trading sentiment.\n\n"
        if context:
            prompt += f"Context: {context}\n\n"

        prompt += f"Text: {text}\n\n"
        prompt += """
Provide:
1. Sentiment: bullish, bearish, or neutral
2. Score: -1 (very bearish) to 1 (very bullish)
3. Confidence: 0 to 1
4. Brief reasoning

Format as JSON:
{
  "sentiment": "bullish|bearish|neutral",
  "score": 0.0,
  "confidence": 0.0,
  "reasoning": "..."
}
"""

        messages = [
            {
                "role": "system",
                "content": "You are a financial analyst expert at interpreting market sentiment.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = await self.chat_completion(
                messages=messages,
                temperature=0.3,  # Low temp for consistency
                max_tokens=300,
            )

            content = response["choices"][0]["message"]["content"]

            # Try to parse JSON from response
            # Sometimes the model wraps JSON in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            logger.info(f"Sentiment analysis: {result['sentiment']} ({result['score']:.2f})")

            return result

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}",
            }

    async def get_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small",
    ) -> List[float]:
        """
        Get text embedding.

        Args:
            text: Text to embed
            model: Embedding model

        Returns:
            Embedding vector
        """
        if not self.api_key:
            raise ExecutionError("OpenAI API key not configured")

        payload = {
            "model": model,
            "input": text,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]

    async def summarize_market_news(
        self,
        articles: List[str],
        max_articles: int = 5,
    ) -> str:
        """
        Summarize multiple news articles into key trading insights.

        Args:
            articles: List of article texts
            max_articles: Maximum articles to process

        Returns:
            Summary with key insights
        """
        # Truncate articles if too many
        articles = articles[:max_articles]

        combined = "\n\n---\n\n".join(
            f"Article {i+1}:\n{article[:500]}"
            for i, article in enumerate(articles)
        )

        messages = [
            {
                "role": "system",
                "content": "You are a financial analyst. Summarize market news into actionable trading insights.",
            },
            {
                "role": "user",
                "content": f"Summarize these news articles:\n\n{combined}\n\nProvide 3-5 bullet points with key trading insights.",
            },
        ]

        try:
            response = await self.chat_completion(
                messages=messages,
                temperature=0.5,
                max_tokens=400,
            )

            summary = response["choices"][0]["message"]["content"]
            logger.info("Generated market news summary")
            return summary

        except Exception as e:
            logger.error(f"News summarization failed: {e}")
            return f"Failed to summarize news: {str(e)}"

    async def analyze_text(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 300,
        purpose: str = "Text Analysis",
    ) -> str:
        """
        Analyze text with AI and return raw response.

        Args:
            prompt: The prompt to analyze
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            purpose: Description of what this analysis is for (for logging)

        Returns:
            Raw text response from AI
        """
        messages = [
            {
                "role": "system",
                "content": "You are a financial analyst expert at interpreting market news and sentiment.",
            },
            {"role": "user", "content": prompt},
        ]

        model = "gpt-4o-mini"

        try:
            response = await self.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                model=model,
            )

            content = response["choices"][0]["message"]["content"]

            # Calculate tokens and cost
            tokens_used = response.get("usage", {}).get("total_tokens", 0)
            # gpt-4o-mini pricing: $0.150 per 1M input tokens, $0.600 per 1M output tokens
            input_tokens = response.get("usage", {}).get("prompt_tokens", 0)
            output_tokens = response.get("usage", {}).get("completion_tokens", 0)
            cost_usd = (input_tokens * 0.150 / 1_000_000) + (output_tokens * 0.600 / 1_000_000)

            # Log the conversation
            full_prompt = f"SYSTEM: {messages[0]['content']}\n\nUSER: {prompt}"
            self._log_conversation(
                model=model,
                purpose=purpose,
                prompt=full_prompt,
                response=content,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                temperature=temperature,
                max_tokens=max_tokens
            )

            logger.info(f"OpenAI {purpose}: {tokens_used} tokens, ${cost_usd:.4f}")

            return content

        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return f"Analysis failed: {str(e)}"

    async def generate_trading_signal(
        self,
        data: Dict[str, Any],
        strategy_context: str,
    ) -> Dict[str, Any]:
        """
        Generate trading signal using AI analysis.

        Args:
            data: Market data and indicators
            strategy_context: Description of the trading strategy

        Returns:
            {
                "action": "buy" | "sell" | "hold",
                "confidence": float (0 to 1),
                "reasoning": str
            }
        """
        prompt = f"""
Strategy Context: {strategy_context}

Current Market Data:
{json.dumps(data, indent=2)}

Based on this data and strategy, provide a trading recommendation.

Format as JSON:
{{
  "action": "buy|sell|hold",
  "confidence": 0.0-1.0,
  "reasoning": "..."
}}
"""

        messages = [
            {
                "role": "system",
                "content": "You are a quantitative trading analyst.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = await self.chat_completion(
                messages=messages,
                temperature=0.2,
                max_tokens=300,
            )

            content = response["choices"][0]["message"]["content"]

            # Parse JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            logger.info(f"AI signal: {result['action']} ({result['confidence']:.2f})")

            return result

        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return {
                "action": "hold",
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}",
            }
