#!/usr/bin/env python3
"""
Test script for market-wide monitoring features.

Tests:
1. Market-wide news scanning (no symbol filter)
2. Macro news analysis (Fed, inflation, geopolitics)
3. VIX spike detection
4. Index monitoring (SPY, QQQ, VIX)
"""
import asyncio
import sys
import os

# Add optifire to path
sys.path.insert(0, '/root/optifire')

from optifire.services.news_scanner import NewsScanner
from optifire.exec.broker_alpaca import AlpacaBroker


async def test_market_wide_news():
    """Test market-wide news scanning."""
    print("=" * 60)
    print("TEST 1: Market-Wide News Scanning")
    print("=" * 60)

    scanner = NewsScanner()

    # Get market-wide news (no symbol filter)
    print("\n📰 Fetching market-wide news (no symbol filter)...\n")
    articles = await scanner.get_latest_news(symbol=None, hours_back=6)

    print(f"Found {len(articles)} market-wide articles:")
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article['headline']}")
        print(f"   Source: {article['source']}")
        print(f"   Time: {article['timestamp']}")
        if article.get('symbols'):
            print(f"   Related: {', '.join(article['symbols'][:3])}")

    return len(articles) > 0


async def test_macro_news_analysis():
    """Test macro news analysis."""
    print("\n" + "=" * 60)
    print("TEST 2: Macro News Analysis (Fed, Inflation, Geopolitics)")
    print("=" * 60)

    scanner = NewsScanner()

    print("\n🌍 Analyzing macro news for systemic signals...\n")
    analysis = await scanner.analyze_macro_news()

    print(f"Market Regime: {analysis['market_regime']}")
    print(f"Confidence: {analysis['confidence']:.0%}")
    print(f"Recommended Action: {analysis['action']}")
    print(f"Reason: {analysis['reason']}")
    print(f"Affected Sectors: {', '.join(analysis['affected_sectors'])}")

    if analysis['action'] == 'DEFENSIVE':
        print("\n⚠️  System would reduce exposure by 50%")
    elif analysis['action'] == 'AGGRESSIVE':
        print("\n🚀 System would increase exposure by 30%")

    return True


async def test_vix_monitoring():
    """Test VIX spike detection."""
    print("\n" + "=" * 60)
    print("TEST 3: VIX Spike Detection")
    print("=" * 60)

    broker = AlpacaBroker(paper=True)

    print("\n📊 Fetching current VIX level...\n")

    try:
        vix_quote = await broker.get_quote("VIX")
        vix_level = float(vix_quote.get("ap", 0))

        print(f"Current VIX: {vix_level:.1f}")

        # Determine regime
        if vix_level < 15:
            regime = "LOW (calm markets)"
            exposure = "120%"
        elif vix_level < 25:
            regime = "NORMAL"
            exposure = "100%"
        elif vix_level < 35:
            regime = "ELEVATED (caution)"
            exposure = "70%"
        else:
            regime = "CRISIS (extreme fear)"
            exposure = "30%"

        print(f"VIX Regime: {regime}")
        print(f"Recommended Exposure: {exposure}")

        if vix_level > 30:
            print("\n🚨 HIGH VIX WARNING - System would trigger defensive mode!")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_index_monitoring():
    """Test index monitoring (SPY, QQQ)."""
    print("\n" + "=" * 60)
    print("TEST 4: Index Monitoring (SPY, QQQ, VIX)")
    print("=" * 60)

    broker = AlpacaBroker(paper=True)

    print("\n📊 Fetching index data...\n")

    try:
        spy_quote = await broker.get_quote("SPY")
        qqq_quote = await broker.get_quote("QQQ")
        vix_quote = await broker.get_quote("VIX")

        spy_price = float(spy_quote.get("ap", 0))
        qqq_price = float(qqq_quote.get("ap", 0))
        vix_price = float(vix_quote.get("ap", 0))

        print(f"SPY (S&P 500): ${spy_price:.2f}")
        print(f"QQQ (Nasdaq): ${qqq_price:.2f}")
        print(f"VIX (Fear Index): {vix_price:.1f}")

        # Check market stress
        if vix_price > 25:
            print("\n⚠️  MARKET STRESS DETECTED - VIX above 25")
            print("   System monitoring for defensive opportunities (TLT, GLD)")
        else:
            print("\n✅ Market conditions normal")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MARKET-WIDE MONITORING TEST SUITE")
    print("=" * 60)
    print("\nTesting new features:")
    print("1. Market-wide news scanning")
    print("2. Macro news analysis (Fed, inflation, geopolitics)")
    print("3. VIX spike detection")
    print("4. Index monitoring (SPY, QQQ, VIX)")
    print("\n")

    results = []

    # Test 1: Market-wide news
    try:
        result = await test_market_wide_news()
        results.append(("Market-wide news", result))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Market-wide news", False))

    # Test 2: Macro analysis
    try:
        result = await test_macro_news_analysis()
        results.append(("Macro analysis", result))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Macro analysis", False))

    # Test 3: VIX monitoring
    try:
        result = await test_vix_monitoring()
        results.append(("VIX monitoring", result))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("VIX monitoring", False))

    # Test 4: Index monitoring
    try:
        result = await test_index_monitoring()
        results.append(("Index monitoring", result))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Index monitoring", False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Market-wide monitoring is working!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    asyncio.run(main())
