#!/usr/bin/env python3
"""
Debug script to analyze NVO data using the modular implementation.
"""

import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from data.data_loader import DataLoader
from data.currency_converter import CurrencyConverter
from valuation_calculator_modular import ValuationCalculator

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
    
    # Load and convert using modular system
    print("\n=== MODULAR SYSTEM ANALYSIS ===")
    data_loader = DataLoader(Path(__file__).parent.parent / 'data')
    company_data = data_loader.load_company_data('NVO')
    
    # Check modular conversion
    ttm_usd = company_data.financial_history['TTM']
    print(f"Modular converted TTM FCF (USD): {ttm_usd.free_cash_flow:,.2f}")
    print(f"Modular converted TTM Revenue (USD): {ttm_usd.revenue:,.2f}")
    print(f"Modular converted TTM Net Income (USD): {ttm_usd.net_income:,.2f}")
    
    # Check modular currency conversion directly
    print("\n=== DIRECT CURRENCY CONVERTER ===")
    modular_normalized = CurrencyConverter.convert_to_usd(raw_data)
    modular_ttm = modular_normalized['financialHistory']['TTM']
    print(f"Direct converted TTM FCF (USD): {modular_ttm['freeCashFlow']:,.2f}")
    print(f"Direct converted TTM Revenue (USD): {modular_ttm['revenue']:,.2f}")
    print(f"Direct converted TTM Net Income (USD): {modular_ttm['netIncome']:,.2f}")
    
    # Check historical data for growth calculation
    print("\n=== HISTORICAL FCF FOR GROWTH CALCULATION ===")
    years = ['2020', '2021', '2022', '2023', '2024', 'TTM']
    print("Modular FCF history (USD):")
    for year in years:
        if year in company_data.financial_history:
            year_data = company_data.financial_history[year]
            print(f"  {year}: {year_data.free_cash_flow:,.2f}")
    
    # Run full valuation to see results
    print("\n=== FULL VALUATION RESULTS ===")
    calculator = ValuationCalculator(company_data)
    results = calculator.calculate_intrinsic_value()
    print(f"Intrinsic Value: ${results['intrinsicValue']:.2f}")
    print(f"Current Price: ${results['currentPrice']:.2f}")
    print(f"Upside: {results['upside']:.1f}%")

if __name__ == "__main__":
    main()
