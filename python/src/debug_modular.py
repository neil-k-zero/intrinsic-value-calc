#!/usr/bin/env python3
"""
Debug script to test modular components step by step.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_step_by_step():
    """Test each component step by step."""
    
    print("🔍 Testing Step by Step...")
    
    try:
        print("Step 1: Testing currency converter...")
        from data.currency_converter import CurrencyConverter
        
        # Test with NVO-like data
        test_data = {
            'currency': 'DKK',
            'exchangeRate': {
                'usdToDkk': 6.9,
                'dkkToUsd': 0.1449
            },
            'financialHistory': {
                '2024': {
                    'revenue': 1000,  # 1000 DKK
                    'netIncome': 100   # 100 DKK
                }
            }
        }
        
        converted = CurrencyConverter.convert_to_usd(test_data)
        print(f"✅ Currency conversion works")
        print(f"   Original revenue: {test_data['financialHistory']['2024']['revenue']} DKK")
        print(f"   Converted revenue: {converted['financialHistory']['2024']['revenue']:.2f} USD")
        
    except Exception as e:
        print(f"❌ Currency converter failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("\nStep 2: Testing data loader...")
        from data.data_loader import DataLoader
        
        loader = DataLoader(DataLoader.get_default_data_directory())
        company_data = loader.load_company_data('NVO')
        
        print(f"✅ Data loading works")
        print(f"   Company: {company_data.company_name}")
        print(f"   Currency: {company_data.currency}")
        print(f"   Current Price: ${company_data.get_current_price()}")
        
    except Exception as e:
        print(f"❌ Data loader failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("\nStep 3: Testing individual valuation methods...")
        from valuation.dcf_valuation import DCFValuation
        
        dcf = DCFValuation(company_data)
        fcfe_result = dcf.calculate_fcfe()
        
        print(f"✅ DCF valuation works")
        print(f"   FCFE method: {fcfe_result.method}")
        print(f"   Not applicable: {fcfe_result.not_applicable}")
        if not fcfe_result.not_applicable:
            print(f"   Value per share: ${fcfe_result.value_per_share:.2f}")
        else:
            print(f"   Reason: {fcfe_result.reason}")
        
    except Exception as e:
        print(f"❌ DCF valuation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("\nStep 4: Testing full calculator...")
        from valuation_calculator_modular import ValuationCalculator
        
        calculator = ValuationCalculator(company_data)
        results = calculator.calculate_intrinsic_value()
        
        print(f"✅ Full calculator works")
        print(f"   Intrinsic Value: ${results['intrinsicValue']:.2f}")
        print(f"   Current Price: ${results['currentPrice']:.2f}")
        print(f"   Upside: {results['upside']:.1f}%")
        
    except Exception as e:
        print(f"❌ Full calculator failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 All tests passed!")
    return True

if __name__ == '__main__':
    success = test_step_by_step()
    sys.exit(0 if success else 1)
