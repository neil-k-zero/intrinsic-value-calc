#!/usr/bin/env python3
"""
Debug script to check EBITDA calculation differences.
"""

import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from valuation_calculator import ValuationCalculator as OriginalCalculator

def main():
    # Load raw NVO data
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
    
    # Check original calculator's EV/EBITDA calculation
    original_calc = OriginalCalculator(raw_data)
    ev_ebitda_result = original_calc.calculate_ev_ebitda_valuation()
    
    print(f"\n=== ORIGINAL EV/EBITDA RESULT ===")
    print(f"Value per share: {ev_ebitda_result.get('valuePerShare', 'N/A')}")
    print(f"Not applicable: {ev_ebitda_result.get('notApplicable', False)}")
    if ev_ebitda_result.get('notApplicable'):
        print(f"Reason: {ev_ebitda_result.get('reason', 'Unknown')}")
    
    # Check what the original uses for EBITDA calculation
    normalized_data = original_calc.normalized_data
    ttm_normalized = normalized_data['financialHistory']['TTM']
    
    print(f"\n=== ORIGINAL NORMALIZED DATA ===")
    if 'ebitda' in ttm_normalized:
        print(f"TTM EBITDA (USD): {ttm_normalized['ebitda']:,.2f}")
    
    # Calculate EBITDA manually if needed
    operating_income = ttm_normalized.get('operatingIncome', 0)
    depreciation = ttm_normalized.get('depreciation', 0)
    manual_ebitda = operating_income + depreciation
    
    print(f"Operating Income (USD): {operating_income:,.2f}")
    print(f"Depreciation (USD): {depreciation:,.2f}")
    print(f"Manual EBITDA (USD): {manual_ebitda:,.2f}")

if __name__ == "__main__":
    main()
