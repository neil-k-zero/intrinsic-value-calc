#!/usr/bin/env python3
"""
Debug script to check EBITDA calculation differences.
"""

import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from data.data_loader import DataLoader
from valuation_calculator_modular import ValuationCalculator

def main():
    # Load data using the new modular system
    data_path = Path(__file__).parent.parent / 'data' / 'nvo.json'
    with open(data_path, 'r') as f:
        raw_data = json.load(f)
    
    # Check what EBITDA data is available
    print("=== EBITDA IN RAW DATA ===")
    ttm_data = raw_data['financialHistory']['TTM']
    print(f"TTM financial fields: {list(ttm_data.keys())}")
    
    if 'ebitda' in ttm_data:
        print(f"TTM EBITDA (DKK): {ttm_data['ebitda']:,}")
    else:
        print("No explicit EBITDA field found")
    
    # Load and process data using modular system
    data_loader = DataLoader(Path(__file__).parent.parent / 'data')
    company_data = data_loader.load_company_data('NVO')
    
    # Check modular calculator's EV/EBITDA calculation
    modular_calc = ValuationCalculator(company_data)
    results = modular_calc.calculate_intrinsic_value()
    relative_breakdown = results['valuationBreakdown']['relative']
    ev_ebitda_result = relative_breakdown['evEbitdaValuation']
    
    print(f"\n=== MODULAR EV/EBITDA RESULT ===")
    print(f"Value per share: {ev_ebitda_result.get('valuePerShare', 'N/A')}")
    print(f"Not applicable: {ev_ebitda_result.get('notApplicable', False)}")
    if ev_ebitda_result.get('notApplicable'):
        print(f"Reason: {ev_ebitda_result.get('reason', 'Unknown')}")
    
    # Check what the modular system uses for EBITDA calculation
    ttm_usd = company_data.financial_history['TTM']
    
    print(f"\n=== MODULAR NORMALIZED DATA ===")
    if hasattr(ttm_usd, 'ebitda') and ttm_usd.ebitda:
        print(f"TTM EBITDA (USD): {ttm_usd.ebitda:,.2f}")
    
    # Calculate EBITDA manually if needed
    operating_income = getattr(ttm_usd, 'operating_income', 0) or 0
    depreciation = getattr(ttm_usd, 'depreciation', 0) or 0
    manual_ebitda = operating_income + depreciation
    
    print(f"Operating Income (USD): {operating_income:,.2f}")
    print(f"Depreciation (USD): {depreciation:,.2f}")
    print(f"Manual EBITDA (USD): {manual_ebitda:,.2f}")

if __name__ == "__main__":
    main()
