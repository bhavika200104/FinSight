# test_persistence.py

from persistence import save_investments, load_investments
import os
import json

# Step 1: Define test data
test_data = {
    "AAPL": {"amount_invested": 1000},
    "GOOGL": {"amount_invested": 1500},
    "MSFT": {"amount_invested": 1200}
}

# Step 2: Save test data
print("Saving test data...")
save_investments(test_data)

# Step 3: Load data back
print("Loading data back...")
loaded_data = load_investments()

# Step 4: Compare
print("Verifying data integrity...")
if test_data == loaded_data:
    print("✅ SUCCESS: Data was saved and loaded correctly.")
else:
    print("❌ ERROR: Data mismatch.")
    print("Expected:", test_data)
    print("Got:     ", loaded_data)

# Optional: Inspect file
print("\nRaw content in data/portfolio.json:")
with open("data/portfolio.json", "r") as f:
    print(f.read())
