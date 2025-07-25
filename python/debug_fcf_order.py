#!/usr/bin/env python3
"""
Debug script to check FCF series order and growth calculation.
"""

import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from data.data_loader import DataLoader
from utils.financial_calculations import FinancialCalculations

def main():
    # Load data using modular approach
    data_loader = DataLoader(Path(__file__).parent.parent / 'data')
    company_data = data_loader.load_company_data('nvo')
    
    print("=== COMPANY DATA DEBUG ===")
    print(f"Currency: {company_data.currency}")
    
    # Check FCF series
    fcf_series = company_data.get_financial_series('freeCashFlow', 6)
    print(f"\nFCF Series (from get_financial_series):")
    for year, value in fcf_series.items():
        print(f"  {year}: {value:,.2f}")
    
    # Get the values as a list (this is what goes to CAGR calculation)
    fcf_values = [value for value in fcf_series.values() if value is not None]
    print(f"\nFCF Values for CAGR: {fcf_values}")
    
    # Calculate CAGR
    calc = FinancialCalculations(company_data)
    growth_rate = calc.calculate_cagr(fcf_values)
    print(f"Calculated CAGR: {growth_rate:.4f} ({growth_rate*100:.2f}%)")
    
    # Check if this makes sense manually
    if len(fcf_values) >= 2:
        beginning_value = fcf_values[0] 
        ending_value = fcf_values[-1]
        periods = len(fcf_values) - 1
        manual_cagr = ((ending_value / beginning_value) ** (1/periods)) - 1
        print(f"Manual CAGR check: {manual_cagr:.4f} ({manual_cagr*100:.2f}%)")
        print(f"  Beginning value: {beginning_value:,.2f}")
        print(f"  Ending value: {ending_value:,.2f}")
        print(f"  Periods: {periods}")

if __name__ == "__main__":
    main()
