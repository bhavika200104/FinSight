from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify, get_flashed_messages
from flask_cors import CORS
from portfolio import Portfolio
from utils import get_multiple_stock_prices, StockPriceError

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key
CORS(app)

portfolio = Portfolio()

# In-memory user store for demo (replace with persistent storage in production)
users = {}

@app.route("/", methods=["GET"])
def index():
    summary = portfolio.get_portfolio_summary()
    total_invested = portfolio.calculate_total_invested()
    current_value = portfolio.calculate_current_value()
    profit_loss = portfolio.calculate_profit_loss()
    return render_template(
        "view_portfolio.html",
        portfolio=summary,
        total_invested=total_invested,
        current_value=current_value,
        profit_loss=profit_loss
    )

@app.route("/add", methods=["GET"])
def add_form():
    return render_template("add.html")

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

@app.route("/remove", methods=["GET"])
def remove_form():
    return render_template("remove.html")

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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Check against users dictionary
        if username in users and users[username]["password"] == password:
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Add more fields as needed
        if username in users:
            flash("Username already exists. Please choose another.", "error")
            return redirect(url_for("signup"))
        users[username] = {"password": password}
        flash("Signup successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)