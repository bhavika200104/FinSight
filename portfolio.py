from utils import get_stock_price, get_stock_info, validate_ticker, StockPriceError
from persistence import load_investments, save_investments


class Portfolio:
    def __init__(self):
        # investments dict: key = ticker, value = dict with amount invested and optionally other data
        self.investments = load_investments()

    def add_investment(self, ticker, amount_invested):
        ticker = ticker.upper().strip()
        if not validate_ticker(ticker):
            raise ValueError(f"Invalid ticker symbol: {ticker}")
        
        if ticker in self.investments:
            self.investments[ticker]['amount_invested'] += amount_invested
        else:
            self.investments[ticker] = {'amount_invested': amount_invested}
        save_investments(self.investments)

    def remove_investment(self, ticker):
        ticker = ticker.upper().strip()
        if ticker in self.investments:
            del self.investments[ticker]
        else:
            raise KeyError(f"{ticker} not found in portfolio")
        save_investments(self.investments)
    def calculate_total_invested(self):
        return sum(data['amount_invested'] for data in self.investments.values())

    def calculate_current_value(self):
        total_value = 0
        for ticker in self.investments:
            try:
                price = get_stock_price(ticker)
                self.investments[ticker]['current_price'] = price
                # Assume 1 unit for simplicity, or you can extend for quantity if needed
                total_value += price
            except StockPriceError:
                self.investments[ticker]['current_price'] = None
        return total_value

    def calculate_profit_loss(self):
        current_value = self.calculate_current_value()
        invested = self.calculate_total_invested()
        return current_value - invested

    def get_portfolio_summary(self):
        summary = {}
        for ticker, data in self.investments.items():
            try:
                stock_info = get_stock_info(ticker)
                summary[ticker] = {
                    'name': stock_info.get('name', ticker),
                    'current_price': stock_info.get('price'),
                    'currency': stock_info.get('currency', 'USD'),
                    'change': stock_info.get('change', 0),
                    'change_percent': stock_info.get('change_percent', 0),
                    'amount_invested': data['amount_invested'],
                    'profit_loss_per_stock': (stock_info.get('price') or 0) - data['amount_invested']
                }
            except StockPriceError as e:
                summary[ticker] = {
                    'error': str(e),
                    'amount_invested': data['amount_invested']
                }
        return summary


if __name__ == "__main__":
    # Simple interactive test
    p = Portfolio()

    print("Adding investments:")
    try:
        p.add_investment("AAPL", 1000)
        p.add_investment("GOOGL", 1500)
        p.add_investment("MSFT", 1200)
        print("Added AAPL, GOOGL, MSFT")
    except ValueError as ve:
        print("Error:", ve)

    print("\nCurrent Portfolio Summary:")
    summary = p.get_portfolio_summary()
    for ticker, info in summary.items():
        if 'error' in info:
            print(f"{ticker}: Error - {info['error']}")
        else:
            print(f"{ticker}: Invested: {info['amount_invested']}, Current Price: {info['current_price']}, P/L: {info['profit_loss_per_stock']}")

    print("\nTotal Invested:", p.calculate_total_invested())
    print("Current Value:", p.calculate_current_value())
    print("Total Profit/Loss:", p.calculate_profit_loss())

    print("\nRemoving GOOGL...")
    try:
        p.remove_investment("GOOGL")
    except KeyError as ke:
        print("Error:", ke)

    print("\nPortfolio Summary After Removal:")
    summary = p.get_portfolio_summary()
    for ticker, info in summary.items():
        if 'error' in info:
            print(f"{ticker}: Error - {info['error']}")
        else:
            print(f"{ticker}: Invested: {info['amount_invested']}, Current Price: {info['current_price']}, P/L: {info['profit_loss_per_stock']}")

    print("\nFinal Total Invested:", p.calculate_total_invested())
    print("Final Current Value:", p.calculate_current_value())
    print("Final Total Profit/Loss:", p.calculate_profit_loss())
