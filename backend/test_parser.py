"""
Test script for the Invoice Parser API
"""
import requests
import json

from parser import InvoiceParser

BASE_URL = "http://localhost:8000"


def test_single_text():
    """Test with a single text input."""
    url = f"{BASE_URL}/parse"

    # This should work even with newlines
    payload = {
        "data": "Al Noor Traders Invoice #88912\nSugar – Rs. 6,000 (50 kg)\nWheat Flour (10kg @ 950)\nCooking Oil: Qty 5 bottles Price 1200/bottle"
    }

    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


def test_array_input():
    """Test with array of texts."""
    url = f"{BASE_URL}/parse"

    payload = {
        "data": [
            "Sugar – Rs. 6,000 (50 kg)",
            "Wheat Flour (10kg @ 950)",
            "Cooking Oil: Qty 5 bottles Price 1200/bottle"
        ]
    }

    response = requests.post(url, json=payload)
    print(f"\nArray Test - Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_raw_endpoint():
    """Test the raw endpoint for problematic inputs."""
    url = f"{BASE_URL}/parse/raw"

    # Even more problematic input
    payload = {
        "data": """Al Noor Traders
Invoice #88912
Date: 2023-11-15

Sugar – Rs. 6,000 (50 kg)
Wheat Flour (10kg @ 950)
Cooking Oil: Qty 5 bottles Price 1200/bottle

Total: Rs. 7,750
Tax: Rs. 620
Grand Total: Rs. 8,370

Thank you!"""
    }

    response = requests.post(url, json=payload)
    print(f"\nRaw Endpoint Test - Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")



print("Testing Invoice Parser API...")
print("=" * 50)
# Test single text
test_single_text()

# Test array input
test_array_input()

# Test raw endpoint
test_raw_endpoint()


def test_various_formats():
    """Test parser with various currency formats."""
    parser = InvoiceParser()

    test_cases = [
        # Different currency symbols
        "Sugar – Rs. 6,000 (50 kg)",
        "Sugar – ₹6,000 (50 kg)",
        "Sugar – INR 6000 (50 kg)",
        "Sugar – $60.00 (5 kg)",
        "Sugar – €50.00 (5 kg)",
        "Sugar – £45.00 (5 kg)",

        # Without currency symbols
        "Sugar – 6,000 (50 kg)",
        "Wheat Flour (10kg @ 950)",
        "Wheat Flour (10kg @ Rs. 950)",
        "Wheat Flour (10kg @ ₹950)",

        # Price/unit formats
        "Cooking Oil: Qty 5 bottles Price 1200/bottle",
        "Cooking Oil: Qty 5 bottles Price Rs.1200/bottle",
        "Cooking Oil: Qty 5 bottles Price ₹1200/bottle",

        # Mixed formats
        "Rice 25kg Rs.2500",
        "Rice 25kg ₹2500",
        "Rice 25kg 2500",
        "Rice Rs.2500 25kg",  # Reversed order

        # Unit price formats
        "Tomato 10kg @ 45/kg",
        "Tomato @ Rs.45/kg",
        "Tomato @ ₹45/kg",

        # Complex cases
        "Al Noor Traders Invoice #88912\nSugar – Rs. 6,000 (50 kg)\nWheat Flour (10kg @ 950)\nCooking Oil: Qty 5 bottles Price 1200/bottle",
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test[:50]}...")
        items = parser.parse(test)
        for item in items:
            print(f"  Product: {item.product_name}")
            print(f"  Quantity: {item.quantity} {item.unit}")
            print(f"  Unit Price: {item.unit_price}")
            print(f"  Total Price: {item.total_price}")
            print(f"  Confidence: {item.confidence:.2f}")
