"""
OpenAI client for AI/ML features.
"""
import os
from typing import List, Optional, Dict, Any
import httpx
from datetime import datetime
import json

from optifire.core.logger import logger
from optifire.core.errors import ExecutionError


class OpenAIClient:
    """
    OpenAI API client for sentiment analysis, embeddings, and chat.
    """

    def __init__(self):
        """Initialize OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            logger.warning("OpenAI API key not found in environment")

        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key or ''}",
            "Content-Type": "application/json",
        }

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
