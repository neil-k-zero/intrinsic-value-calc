#!/usr/bin/env python3
"""
Debug script to compare NVO data between original and modular implementations.
"""

import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from valuation_calculator import ValuationCalculator as OriginalCalculator
from data.data_loader import DataLoader
from data.currency_converter import CurrencyConverter

def main():
    # Load raw NVO data
    data_path = Path(__file__).parent.parent / 'data' / 'nvo.json'
    with open(data_path, 'r') as f:
        raw_data = json.load(f)
    
    print("=== RAW DATA ANALYSIS ===")
    print(f"Currency: {raw_data.get('currency')}")
    print(f"Exchange Rate: {raw_data.get('exchangeRate')}")
    
    # Show original financial data (in DKK)
    ttm_data = raw_data['financialHistory']['TTM']
    print(f"\nOriginal TTM FCF (DKK): {ttm_data['freeCashFlow']:,}")
    print(f"Original TTM Revenue (DKK): {ttm_data['revenue']:,}")
    print(f"Original TTM Net Income (DKK): {ttm_data['netIncome']:,}")
    
    # Convert using original method
    print("\n=== ORIGINAL CALCULATOR CONVERSION ===")
    original_calc = OriginalCalculator(raw_data)
    original_normalized = original_calc.normalized_data
    original_ttm = original_normalized['financialHistory']['TTM']
    print(f"Original converted TTM FCF (USD): {original_ttm['freeCashFlow']:,.2f}")
    print(f"Original converted TTM Revenue (USD): {original_ttm['revenue']:,.2f}")
    print(f"Original converted TTM Net Income (USD): {original_ttm['netIncome']:,.2f}")
    
    # Convert using modular method
    print("\n=== MODULAR CONVERTER ===")
    modular_normalized = CurrencyConverter.convert_to_usd(raw_data)
    modular_ttm = modular_normalized['financialHistory']['TTM']
    print(f"Modular converted TTM FCF (USD): {modular_ttm['freeCashFlow']:,.2f}")
    print(f"Modular converted TTM Revenue (USD): {modular_ttm['revenue']:,.2f}")
    print(f"Modular converted TTM Net Income (USD): {modular_ttm['netIncome']:,.2f}")
    
    # Check for differences
    print("\n=== DIFFERENCES ===")
    fcf_diff = original_ttm['freeCashFlow'] - modular_ttm['freeCashFlow']
    print(f"FCF Difference: {fcf_diff:,.2f}")
    
    # Check historical data
    print("\n=== HISTORICAL FCF FOR GROWTH CALCULATION ===")
    years = ['2020', '2021', '2022', '2023', '2024', 'TTM']
    print("Original FCF history (USD):")
    for year in years:
        if year in original_normalized['financialHistory']:
            fcf = original_normalized['financialHistory'][year]['freeCashFlow']
            print(f"  {year}: {fcf:,.2f}")
    
    print("\nModular FCF history (USD):")
    for year in years:
        if year in modular_normalized['financialHistory']:
            fcf = modular_normalized['financialHistory'][year]['freeCashFlow']
            print(f"  {year}: {fcf:,.2f}")

if __name__ == "__main__":
    main()
