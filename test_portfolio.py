import unittest
import os
import json
from portfolio import Portfolio
from utils import validate_ticker

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        """Set up a fresh Portfolio instance before each test."""
        self.portfolio = Portfolio()
        self.test_file = "test_portfolio_data.json"

    def tearDown(self):
        """Clean up after tests by removing the test file."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_investment(self):
        """Test adding investments to the portfolio."""
        self.portfolio.add_investment("AAPL", 1000)
        self.assertIn("AAPL", self.portfolio.investments)
        self.assertEqual(self.portfolio.investments["AAPL"]["amount_invested"], 1000)

        # Add more to the same investment
        self.portfolio.add_investment("AAPL", 500)
        self.assertEqual(self.portfolio.investments["AAPL"]["amount_invested"], 1500)

    def test_remove_investment(self):
        """Test removing investments from the portfolio."""
        self.portfolio.add_investment("AAPL", 1000)
        self.portfolio.remove_investment("AAPL")
        self.assertNotIn("AAPL", self.portfolio.investments)

        # Test removing a non-existent investment
        with self.assertRaises(KeyError):
            self.portfolio.remove_investment("GOOGL")

    def test_calculate_total_invested(self):
        """Test calculating the total amount invested."""
        self.portfolio.add_investment("AAPL", 1000)
        self.portfolio.add_investment("GOOGL", 1500)
        self.assertEqual(self.portfolio.calculate_total_invested(), 2500)

    def test_validate_ticker(self):
        """Test ticker validation (mocked from utils)."""
        self.assertTrue(validate_ticker("AAPL"))
        self.assertFalse(validate_ticker("INVALID"))

if __name__ == "__main__":
    unittest.main()
