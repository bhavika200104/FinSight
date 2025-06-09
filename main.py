from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from portfolio import Portfolio
from utils import get_multiple_stock_prices, StockPriceError

app = Flask(__name__)
CORS(app)

portfolio = Portfolio()

@app.route("/", methods=["GET"])
def index():
    summary = portfolio.get_portfolio_summary()
    total_invested = portfolio.calculate_total_invested()
    current_value = portfolio.calculate_current_value()
    profit_loss = portfolio.calculate_profit_loss()
    return jsonify({
        "portfolio": summary,
        "total_invested": total_invested,
        "current_value": current_value,
        "profit_loss": profit_loss
    })

@app.route("/add", methods=["POST"])
def add_investment():
    data = request.get_json()
    ticker = data.get("ticker")
    amount = data.get("amount")
    if not ticker or amount is None:
        return jsonify({"error": "Missing ticker or amount"}), 400
    try:
        portfolio.add_investment(ticker, float(amount))
        return jsonify({"message": f"Added {ticker} with amount {amount}"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

@app.route("/remove", methods=["POST"])
def remove_investment():
    data = request.get_json()
    ticker = data.get("ticker")
    if not ticker:
        return jsonify({"error": "Missing ticker"}), 400
    try:
        portfolio.remove_investment(ticker)
        return jsonify({"message": f"Removed {ticker}"}), 200
    except KeyError as ke:
        return jsonify({"error": str(ke)}), 404

@app.route("/prices", methods=["POST"])
def get_prices():
    data = request.get_json()
    tickers = data.get("tickers")
    if not tickers or not isinstance(tickers, list):
        return jsonify({"error": "Missing or invalid tickers list"}), 400
    try:
        prices = get_multiple_stock_prices(tickers)
        return jsonify(prices)
    except StockPriceError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)