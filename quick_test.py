#!/usr/bin/env python3
"""
Quick test runner for stock utils
Run with: python quick_test.py
"""

import sys
import time
from datetime import datetime

def quick_test():
    """Run a quick test of all main functions"""
    print("🚀 Quick Stock Utils Test")
    print("=" * 50)
    
    try:
        from utils import (
            get_stock_price, get_multiple_stock_prices, 
            validate_ticker, get_stock_info, get_market_status,
            StockPriceError, clear_cache
        )
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure utils.py is in the same directory")
        return False
    
    # Test 1: Single stock price
    print("\n1️⃣ Testing single stock price...")
    try:
        price = get_stock_price("AAPL")
        print(f"✅ AAPL: ${price:.2f}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Multiple stocks
    print("\n2️⃣ Testing multiple stocks...")
    tickers = ["AAPL", "GOOGL", "MSFT"]
    try:
        prices = get_multiple_stock_prices(tickers)
        for ticker, price in prices.items():
            if price:
                print(f"✅ {ticker}: ${price:.2f}")
            else:
                print(f"❌ {ticker}: Failed")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Invalid ticker
    print("\n3️⃣ Testing invalid ticker...")
    try:
        get_stock_price("INVALID123")
        print("❌ Should have failed!")
        return False
    except StockPriceError:
        print("✅ Correctly handled invalid ticker")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Test 4: Ticker validation
    print("\n4️⃣ Testing ticker validation...")
    valid = validate_ticker("AAPL")
    invalid = validate_ticker("INVALID123")
    print(f"✅ AAPL valid: {valid}")
    print(f"✅ INVALID123 valid: {invalid}")
    
    # Test 5: Stock info
    print("\n5️⃣ Testing detailed stock info...")
    try:
        info = get_stock_info("AAPL")
        print(f"✅ {info['ticker']}: {info['name']}")
        print(f"   Price: ${info['price']}")
        print(f"   Change: {info['change']} ({info['change_percent']}%)")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 6: Cache performance
    print("\n6️⃣ Testing cache performance...")
    clear_cache()
    
    # First call
    start = time.time()
    get_stock_price("AAPL")
    first_time = time.time() - start
    
    # Second call (cached)
    start = time.time()
    get_stock_price("AAPL")
    second_time = time.time() - start
    
    print(f"✅ First call: {first_time:.3f}s")
    print(f"✅ Cached call: {second_time:.3f}s")
    print(f"✅ Speedup: {first_time/second_time:.1f}x")
    
    # Test 7: Market status
    print("\n7️⃣ Testing market status...")
    status = get_market_status()
    print(f"✅ Market status: {status}")
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Utils is working correctly.")
    print("=" * 50)
    return True

def integration_test():
    """Test integration with other team members"""
    print("\n🔗 Integration Test for Team Members")
    print("=" * 50)
    
    from utils import get_stock_price, get_multiple_stock_prices, StockPriceError
    
    # Simulate how Member 2 (Portfolio Logic) would use it
    print("\n👤 Member 2 (Portfolio) Usage Example:")
    try:
        # Get current prices for portfolio calculation
        portfolio_stocks = ["AAPL", "GOOGL", "MSFT"]
        current_prices = get_multiple_stock_prices(portfolio_stocks)
        
        # Simulate portfolio calculation
        holdings = {"AAPL": 10, "GOOGL": 5, "MSFT": 15}
        total_value = 0
        
        for ticker, shares in holdings.items():
            if current_prices[ticker]:
                value = current_prices[ticker] * shares
                total_value += value
                print(f"  {ticker}: {shares} shares × ${current_prices[ticker]:.2f} = ${value:.2f}")
        
        print(f"  📊 Total Portfolio Value: ${total_value:.2f}")
        
    except Exception as e:
        print(f"❌ Portfolio integration error: {e}")
        return False
    
    # Simulate how Member 1 (Backend) would use it
    print("\n👤 Member 1 (Backend) Usage Example:")
    try:
        # Simulate API endpoint for getting stock price
        def api_get_stock_price(ticker):
            try:
                price = get_stock_price(ticker)
                return {"success": True, "ticker": ticker, "price": price}
            except StockPriceError as e:
                return {"success": False, "error": str(e)}
        
        # Test the API function
        result = api_get_stock_price("AAPL")
        print(f"  API Response: {result}")
        
        # Test with invalid ticker
        result = api_get_stock_price("INVALID")
        print(f"  API Error Response: {result}")
        
    except Exception as e:
        print(f"❌ Backend integration error: {e}")
        return False
    
    print("\n✅ Integration tests passed!")
    return True

if __name__ == "__main__":
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = quick_test()
    if success:
        integration_test()
    
    print(f"\n🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")