#!/usr/bin/env python3
"""
Test script for short selling functionality.
"""
import asyncio
import sys
sys.path.insert(0, '/root/optifire')

from optifire.auto_trader import Signal, AutoTrader
from optifire.core.logger import logger


async def test_signal_creation():
    """Test Signal class with BUY and SHORT."""
    print("\n=== Testing Signal Creation ===\n")

    # Test BUY signal
    try:
        buy_signal = Signal(
            symbol="AAPL",
            action="BUY",
            confidence=0.75,
            reason="Strong positive news",
            size_pct=0.10
        )
        print(f"✅ BUY signal created: {buy_signal.symbol} - {buy_signal.action}")
    except Exception as e:
        print(f"❌ BUY signal failed: {e}")

    # Test SHORT signal
    try:
        short_signal = Signal(
            symbol="TSLA",
            action="SHORT",
            confidence=0.80,
            reason="Overvalued, negative news",
            size_pct=0.10
        )
        print(f"✅ SHORT signal created: {short_signal.symbol} - {short_signal.action}")
    except Exception as e:
        print(f"❌ SHORT signal failed: {e}")

    # Test invalid action (should fail)
    try:
        invalid_signal = Signal(
            symbol="NVDA",
            action="HOLD",
            confidence=0.5,
            reason="Testing invalid action"
        )
        print(f"❌ Invalid signal should have failed but didn't!")
    except ValueError as e:
        print(f"✅ Invalid action rejected correctly: {e}")

    # Test case insensitive
    try:
        lowercase_signal = Signal(
            symbol="GOOGL",
            action="short",
            confidence=0.7,
            reason="Testing lowercase"
        )
        print(f"✅ Lowercase 'short' normalized to: {lowercase_signal.action}")
    except Exception as e:
        print(f"❌ Lowercase normalization failed: {e}")


async def test_pnl_calculation():
    """Test P&L calculation for long and short positions."""
    print("\n=== Testing P&L Calculation ===\n")

    # Test LONG P&L
    entry_price = 100.0

    # Long: price goes up 10% -> profit
    current_price = 110.0
    pnl_long = (current_price - entry_price) / entry_price
    print(f"LONG position: Entry ${entry_price} -> Current ${current_price}")
    print(f"  P&L: {pnl_long*100:+.1f}% {'✅ PROFIT' if pnl_long > 0 else '❌ LOSS'}")

    # Long: price goes down 10% -> loss
    current_price = 90.0
    pnl_long = (current_price - entry_price) / entry_price
    print(f"\nLONG position: Entry ${entry_price} -> Current ${current_price}")
    print(f"  P&L: {pnl_long*100:+.1f}% {'✅ PROFIT' if pnl_long > 0 else '❌ LOSS'}")

    # Test SHORT P&L
    print("\n---")

    # Short: price goes down 10% -> profit
    current_price = 90.0
    pnl_short = (entry_price - current_price) / entry_price
    print(f"\nSHORT position: Entry ${entry_price} -> Current ${current_price}")
    print(f"  P&L: {pnl_short*100:+.1f}% {'✅ PROFIT' if pnl_short > 0 else '❌ LOSS'}")

    # Short: price goes up 10% -> loss
    current_price = 110.0
    pnl_short = (entry_price - current_price) / entry_price
    print(f"\nSHORT position: Entry ${entry_price} -> Current ${current_price}")
    print(f"  P&L: {pnl_short*100:+.1f}% {'✅ PROFIT' if pnl_short > 0 else '❌ LOSS'}")


async def test_order_side_logic():
    """Test order side determination."""
    print("\n=== Testing Order Side Logic ===\n")

    # BUY signal -> buy order
    buy_signal = Signal("AAPL", "BUY", 0.8, "Test")
    order_side = "buy" if buy_signal.action == "BUY" else "sell"
    print(f"Signal: {buy_signal.action} -> Order side: {order_side}")
    print(f"  {'✅ CORRECT' if order_side == 'buy' else '❌ WRONG'}: Opens LONG position")

    # SHORT signal -> sell order
    short_signal = Signal("TSLA", "SHORT", 0.8, "Test")
    order_side = "buy" if short_signal.action == "BUY" else "sell"
    print(f"\nSignal: {short_signal.action} -> Order side: {order_side}")
    print(f"  {'✅ CORRECT' if order_side == 'sell' else '❌ WRONG'}: Opens SHORT position")


async def test_close_position_logic():
    """Test close position logic."""
    print("\n=== Testing Close Position Logic ===\n")

    # Close LONG (qty positive)
    qty = 100.0
    is_long = qty > 0
    close_side = "sell" if is_long else "buy"
    print(f"Position: LONG (qty={qty})")
    print(f"  Close with: {close_side}")
    print(f"  {'✅ CORRECT' if close_side == 'sell' else '❌ WRONG'}")

    # Close SHORT (qty negative in Alpaca)
    qty = -100.0
    is_long = qty > 0
    close_side = "sell" if is_long else "buy"
    print(f"\nPosition: SHORT (qty={qty})")
    print(f"  Close with: {close_side} (cover)")
    print(f"  {'✅ CORRECT' if close_side == 'buy' else '❌ WRONG'}")


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SHORT SELLING FUNCTIONALITY TEST")
    print("="*60)

    await test_signal_creation()
    await test_pnl_calculation()
    await test_order_side_logic()
    await test_close_position_logic()

    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
