import yfinance as yf
import requests
from datetime import datetime, timedelta
import time
import json

# Cache to store recent price lookups
_price_cache = {}
_cache_duration = 300  # 5 minutes in seconds

class StockPriceError(Exception):
    pass

def get_stock_price(ticker):

    ticker = ticker.upper().strip()
    
    # Check cache first
    if _is_price_cached(ticker):
        return _price_cache[ticker]['price']
    
    try:
        # yfinance (primary)
        price = _fetch_price_yfinance(ticker)
        if price:
            _cache_price(ticker, price)
            return price
            
        # Alpha Vantage fallback 
        # price = _fetch_price_alpha_vantage(ticker)
        # if price:
        #     _cache_price(ticker, price)
        #     return price
            
        raise StockPriceError(f"Unable to fetch price for {ticker}")
        
    except Exception as e:
        raise StockPriceError(f"Error fetching price for {ticker}: {str(e)}")

def get_multiple_stock_prices(tickers):

    prices = {}
    for ticker in tickers:
        try:
            prices[ticker] = get_stock_price(ticker)
        except StockPriceError as e:
            print(f"Warning: {e}")
            prices[ticker] = None
    
    return prices

def validate_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return 'regularMarketPrice' in info or 'currentPrice' in info
    except:
        return False

def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="2d")
        
        current_price = info.get('regularMarketPrice') or info.get('currentPrice')
        if not current_price and not hist.empty:
            current_price = hist['Close'].iloc[-1]
        
        prev_close = info.get('regularMarketPreviousClose')
        if not prev_close and len(hist) >= 2:
            prev_close = hist['Close'].iloc[-2]
        
        change = current_price - prev_close if current_price and prev_close else 0
        change_percent = (change / prev_close * 100) if prev_close else 0
        
        return {
            'ticker': ticker.upper(),
            'name': info.get('longName', ticker.upper()),
            'price': round(current_price, 2) if current_price else None,
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'currency': info.get('currency', 'USD'),
            'last_updated': datetime.now().isoformat()
        }
    except Exception as e:
        raise StockPriceError(f"Error fetching info for {ticker}: {str(e)}")

def _fetch_price_yfinance(ticker):
    """Fetch price using yfinance library"""
    try:
        stock = yf.Ticker(ticker)
        
        # Try getting current price from info
        info = stock.info
        price = info.get('regularMarketPrice') or info.get('currentPrice')
        
        if price:
            return float(price)
        
        # Fallback: get latest price from history
        hist = stock.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
            
        return None
        
    except Exception as e:
        print(f"yfinance error for {ticker}: {e}")
        return None

def _fetch_price_alpha_vantage(ticker, api_key=None):

    if not api_key:
        return None
    
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Global Quote' in data:
            price = data['Global Quote']['05. price']
            return float(price)
            
        return None
        
    except Exception as e:
        print(f"Alpha Vantage error for {ticker}: {e}")
        return None

def _is_price_cached(ticker):
    """Check if price is in cache and still valid"""
    if ticker not in _price_cache:
        return False
    
    cache_time = _price_cache[ticker]['timestamp']
    current_time = time.time()
    
    return (current_time - cache_time) < _cache_duration

def _cache_price(ticker, price):
    """Cache the price with timestamp"""
    _price_cache[ticker] = {
        'price': price,
        'timestamp': time.time()
    }

def clear_cache():
    """Clear the price cache"""
    global _price_cache
    _price_cache = {}

def get_market_status():

    try:
        # Use SPY as market indicator
        spy = yf.Ticker("SPY")
        hist = spy.history(period="1d")
        
        if not hist.empty:
            last_update = hist.index[-1]
            now = datetime.now()
            
            # Simple check: if last update is today, market is likely open
            if last_update.date() == now.date():
                return "OPEN"
            else:
                return "CLOSED"
    except:
        pass
    
    return "UNKNOWN"

# Utility functions for error handling
def is_valid_response(price):
    return price is not None and isinstance(price, (int, float)) and price > 0

def format_price(price, currency="USD"):
    if price is None:
        return "N/A"
    
    if currency == "USD":
        return f"${price:.2f}"
    else:
        return f"{price:.2f} {currency}"

# For testing purposes
if __name__ == "__main__":
    # Test the utility functions
    test_tickers = ["AAPL", "GOOGL", "MSFT", "INVALID"]
    
    print("Testing individual stock prices:")
    for ticker in test_tickers:
        try:
            price = get_stock_price(ticker)
            print(f"{ticker}: ${price:.2f}")
        except StockPriceError as e:
            print(f"{ticker}: Error - {e}")
    
    print("\nTesting multiple stock prices:")
    prices = get_multiple_stock_prices(["AAPL", "GOOGL", "MSFT"])
    for ticker, price in prices.items():
        if price:
            print(f"{ticker}: ${price:.2f}")
        else:
            print(f"{ticker}: Failed to fetch")
    
    print(f"\nMarket Status: {get_market_status()}")



# get_stock_price(ticker) - Get single stock price
# get_multiple_stock_prices(tickers) - Get stock prices for multiple tickers
# validate_ticker(ticker) - Check if ticker exists
# get_stock_info(ticker) - Detailed stock data