import unittest
import time
import sys
from unittest.mock import patch, MagicMock
import json

# Import our utils module
try:
    from utils import (
        get_stock_price, get_multiple_stock_prices, validate_ticker,
        get_stock_info, clear_cache, get_market_status, 
        StockPriceError, is_valid_response, format_price,
        _is_price_cached, _cache_price
    )
except ImportError:
    print("Error: Cannot import utils.py. Make sure it's in the same directory.")
    sys.exit(1)

class TestStockPriceFetching(unittest.TestCase):
    """Test cases for stock price fetching functionality"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        clear_cache()  # Clear cache before each test
        self.valid_tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        self.invalid_tickers = ["INVALID123", "FAKE_STOCK", ""]
        
    def tearDown(self):
        """Clean up after each test method."""
        clear_cache()

    def test_get_stock_price_valid_ticker(self):
        """Test fetching price for valid ticker"""
        print("\n Testing valid ticker price fetching...")
        
        for ticker in self.valid_tickers[:2]:  # Test first 2 to save time
            with self.subTest(ticker=ticker):
                try:
                    price = get_stock_price(ticker)
                    self.assertIsInstance(price, (int, float))
                    self.assertGreater(price, 0)
                    print(f" {ticker}: ${price:.2f}")
                except StockPriceError as e:
                    self.fail(f"Failed to fetch price for {ticker}: {e}")

    def test_get_stock_price_invalid_ticker(self):
        """Test fetching price for invalid ticker"""
        print("\n Testing invalid ticker handling...")
        
        for ticker in self.invalid_tickers:
            with self.subTest(ticker=ticker):
                with self.assertRaises(StockPriceError):
                    get_stock_price(ticker)
                print(f" Correctly handled invalid ticker: '{ticker}'")

    def test_price_caching(self):
        """Test price caching functionality"""
        print("\n Testing price caching...")
        
        ticker = "AAPL"
        
        # First call - should fetch from API
        start_time = time.time()
        price1 = get_stock_price(ticker)
        first_call_time = time.time() - start_time
        
        # Second call - should use cache
        start_time = time.time()
        price2 = get_stock_price(ticker)
        second_call_time = time.time() - start_time
        
        # Cached call should be faster and return same price
        self.assertEqual(price1, price2)
        self.assertLess(second_call_time, first_call_time)
        print(f" Cache working: First call {first_call_time:.3f}s, Second call {second_call_time:.3f}s")

    def test_multiple_stock_prices(self):
        """Test fetching multiple stock prices"""
        print("\n Testing multiple stock price fetching...")
        
        test_tickers = ["AAPL", "GOOGL", "INVALID123"]
        prices = get_multiple_stock_prices(test_tickers)
        
        self.assertIsInstance(prices, dict)
        self.assertEqual(len(prices), len(test_tickers))
        
        # Valid tickers should have prices
        for ticker in ["AAPL", "GOOGL"]:
            if ticker in prices and prices[ticker] is not None:
                self.assertGreater(prices[ticker], 0)
                print(f" {ticker}: ${prices[ticker]:.2f}")
        
        # Invalid ticker should be None
        self.assertIsNone(prices.get("INVALID123"))
        print(" Invalid ticker correctly returned None")

    def test_validate_ticker(self):
        """Test ticker validation"""
        print("\n Testing ticker validation...")
        
        # Test valid tickers
        for ticker in self.valid_tickers[:2]:
            is_valid = validate_ticker(ticker)
            print(f" {ticker} validation: {is_valid}")
        
        # Test invalid tickers
        for ticker in self.invalid_tickers:
            is_valid = validate_ticker(ticker)
            self.assertFalse(is_valid)
            print(f" {ticker} correctly identified as invalid")

    def test_get_stock_info(self):
        """Test detailed stock information fetching"""
        print("\n Testing detailed stock info...")
        
        ticker = "AAPL"
        try:
            info = get_stock_info(ticker)
            
            # Check required fields
            required_fields = ['ticker', 'name', 'price', 'change', 'change_percent']
            for field in required_fields:
                self.assertIn(field, info)
            
            # Check data types
            self.assertIsInstance(info['ticker'], str)
            self.assertIsInstance(info['name'], str)
            if info['price'] is not None:
                self.assertIsInstance(info['price'], (int, float))
            
            print(f" Stock Info for {ticker}:")
            print(f"   Name: {info['name']}")
            print(f"   Price: ${info['price']}")
            print(f"   Change: {info['change']} ({info['change_percent']}%)")
            
        except StockPriceError as e:
            self.fail(f"Failed to get stock info for {ticker}: {e}")

    def test_market_status(self):
        """Test market status functionality"""
        print("\n Testing market status...")
        
        status = get_market_status()
        self.assertIn(status, ["OPEN", "CLOSED", "UNKNOWN"])
        print(f" Market Status: {status}")

    def test_utility_functions(self):
        """Test utility helper functions"""
        print("\n Testing utility functions...")
        
        # Test is_valid_response
        self.assertTrue(is_valid_response(100.5))
        self.assertTrue(is_valid_response(1))
        self.assertFalse(is_valid_response(None))
        self.assertFalse(is_valid_response(0))
        self.assertFalse(is_valid_response(-10))
        print(" is_valid_response working correctly")
        
        # Test format_price
        self.assertEqual(format_price(123.456), "$123.46")
        self.assertEqual(format_price(None), "N/A")
        self.assertEqual(format_price(100, "EUR"), "100.00 EUR")
        print(" format_price working correctly")

    def test_error_handling(self):
        """Test error handling with network issues"""
        print("\n Testing error handling...")
        
        # Test with empty string
        with self.assertRaises(StockPriceError):
            get_stock_price("")
        
        # Test with None
        with self.assertRaises((StockPriceError, TypeError)):
            get_stock_price(None)
        
        print(" Error handling working correctly")


class TestStockUtilsIntegration(unittest.TestCase):
    """Integration tests that test the complete workflow"""
    
    def test_portfolio_workflow(self):
        """Test a typical portfolio workflow"""
        print("\n Testing portfolio integration workflow...")
        
        # Simulate adding stocks to portfolio
        portfolio_tickers = ["AAPL", "GOOGL", "MSFT"]
        
        # Get all prices
        prices = get_multiple_stock_prices(portfolio_tickers)
        
        # Calculate portfolio value
        shares = {"AAPL": 10, "GOOGL": 5, "MSFT": 15}
        total_value = 0
        
        for ticker, price in prices.items():
            if price and ticker in shares:
                value = price * shares[ticker]
                total_value += value
                print(f" {ticker}: {shares[ticker]} shares × ${price:.2f} = ${value:.2f}")
        
        print(f" Total Portfolio Value: ${total_value:.2f}")
        self.assertGreater(total_value, 0)

    def test_performance_benchmark(self):
        """Test performance with multiple requests"""
        print("\n Testing performance benchmark...")
        
        tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
        
        # First run - no cache
        clear_cache()
        start_time = time.time()
        prices1 = get_multiple_stock_prices(tickers)
        first_run_time = time.time() - start_time
        
        # Second run - with cache
        start_time = time.time()
        prices2 = get_multiple_stock_prices(tickers)
        second_run_time = time.time() - start_time
        
        print(f" First run (no cache): {first_run_time:.3f}s")
        print(f" Second run (cached): {second_run_time:.3f}s")
        print(f" Speed improvement: {((first_run_time - second_run_time) / first_run_time * 100):.1f}%")
        
        # Cached should be faster
        self.assertLess(second_run_time, first_run_time)


def run_manual_tests():
    """Run manual tests for visual inspection"""
    print("\n" + "="*60)
    print(" MANUAL TESTS - Visual Inspection Required")
    print("="*60)
    
    # Test popular stocks
    popular_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA"]
    print(f"\n Testing Popular Stocks:")
    
    for ticker in popular_stocks:
        try:
            info = get_stock_info(ticker)
            print(f"{ticker:6} | {info['name'][:30]:30} | ${info['price']:8.2f} | {info['change']:+7.2f} ({info['change_percent']:+6.2f}%)")
        except Exception as e:
            print(f"{ticker:6} | ERROR: {str(e)[:50]}")
    
    # Test cache behavior
    print(f"\n⚡ Cache Performance Test:")
    ticker = "AAPL"
    
    times = []
    for i in range(3):
        start = time.time()
        price = get_stock_price(ticker)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"Call {i+1}: ${price:.2f} in {elapsed:.3f}s")
    
    print(f"Cache speedup: {times[0]/times[1]:.1f}x faster")
    
    # Test error cases
    print(f"\n Error Handling Test:")
    error_cases = ["INVALID", "", "123FAKE"]
    for case in error_cases:
        try:
            get_stock_price(case)
            print(f"'{case}': UNEXPECTED SUCCESS")
        except StockPriceError as e:
            print(f"'{case}': Correctly failed - {str(e)[:50]}")


def main():
    """Main test runner"""
    print(" Starting Stock Utils Test Suite")
    print("="*60)
    
    # Check if we can import required modules
    try:
        import yfinance
        import requests
        print(" Required modules available")
    except ImportError as e:
        print(f" Missing required module: {e}")
        print("Run: pip install yfinance requests")
        return
    
    # Run unit tests
    print("\n Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=1)
    
    # Run manual tests
    run_manual_tests()
    
    print("\n" + "="*60)
    print(" Test Suite Completed!")
    print("="*60)


if __name__ == "__main__":
    main()