#!/usr/bin/env python3
"""
Unit tests for the ValuationCalculator class.

This module contains test cases to verify the correctness of the valuation
calculations and ensure the modular implementation works correctly.
"""

import unittest
import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.data_loader import DataLoader
from models.company_data import CompanyData
from valuation_calculator_modular import ValuationCalculator


class TestValuationCalculator(unittest.TestCase):
    """Test cases for the ValuationCalculator class."""
    
    def setUp(self):
        """Set up test data for each test case."""
        # Create mock raw data dictionary
        self.mock_raw_data = {
            'ticker': 'TEST',
            'companyName': 'Test Company',
            'industry': 'Technology',
            'sector': 'Technology',
            'marketData': {
                'currentPrice': 100,
                'marketCap': 10000000000,
                'sharesOutstanding': 100000000,
                'beta': 1.2
            },
            'riskFactors': {
                'riskFreeRate': 0.03,
                'marketRiskPremium': 0.06,
                'specificRiskPremium': 0.01
            },
            'financialHistory': {
                '2024': {
                    'revenue': 1000000000,
                    'netIncome': 100000000,
                    'freeCashFlow': 80000000,
                    'operatingCashFlow': 120000000,
                    'capex': 40000000,
                    'totalDebt': 500000000,
                    'cashAndEquivalents': 50000000,
                    'shareholdersEquity': 800000000,
                    'bookValuePerShare': 8,
                    'eps': 1,
                    'dividend': 0.5,
                    'totalAssets': 1500000000,
                    'operatingIncome': 150000000
                }
            },
            'keyRatios': {
                'valuationRatios': {
                    'peRatio': 20,
                    'pbRatio': 12.5,
                    'evToEbitda': 15
                },
                'leverageRatios': {
                    'debtToEquity': 0.625,
                    'interestCoverage': 15
                },
                'liquidityRatios': {
                    'currentRatio': 1.5
                }
            },
            'assumptions': {
                'terminalGrowthRate': 0.025,
                'taxRate': 0.25,
                'dividendGrowthRate': 0.05
            },
            'growthMetrics': {
                'fcfGrowth5Y': 0.08,
                'revenueGrowth5Y': 0.06
            },
            'industryBenchmarks': {
                'averagePE': 18,
                'averagePB': 3.5
            }
        }
        
        # Convert to CompanyData object using DataLoader
        data_loader = DataLoader()
        self.company_data = data_loader._convert_raw_data_to_company_data(self.mock_raw_data)
        self.calculator = ValuationCalculator(self.company_data)
    
    def test_initialization(self):
        """Test that the calculator initializes correctly."""
        self.assertEqual(self.company_data.ticker, 'TEST')
        self.assertEqual(self.company_data.company_name, 'Test Company')
        self.assertIsNotNone(self.calculator.company_data)
    
    def test_currency_conversion(self):
        """Test currency conversion functionality - data should be in USD."""
        # With modular system, data is pre-converted to USD in CompanyData
        ttm_data = self.company_data.financial_history.get('2024')
        self.assertIsNotNone(ttm_data)
        self.assertGreater(ttm_data.revenue, 0)
        
        # Test DKK conversion
        dkk_data = self.mock_data.copy()
        dkk_data['currency'] = 'DKK'
        dkk_data['exchangeRate'] = {'dkkToUsd': 0.15}
        
        converted_data = self.calculator._convert_to_usd(dkk_data)
        self.assertEqual(converted_data['currency'], 'USD')
        # Revenue should be converted: 1B DKK * 0.15 = 150M USD
        self.assertEqual(converted_data['financialHistory']['2024']['revenue'], 150000000)
    
    def test_cost_of_equity_calculation(self):
        """Test cost of equity calculation using CAPM."""
        cost_of_equity = self.calculator.calculate_cost_of_equity()
        
        # Expected: 0.03 + 1.2 * 0.06 + 0.01 = 0.112 (11.2%)
        expected = 0.03 + 1.2 * 0.06 + 0.01
        self.assertAlmostEqual(cost_of_equity, expected, places=6)
    
    def test_wacc_calculation(self):
        """Test WACC calculation."""
        wacc = self.calculator.calculate_wacc()
        
        # Should be between 0 and 1 (reasonable range for WACC)
        self.assertGreater(wacc, 0)
        self.assertLess(wacc, 1)
        
        # Should be less than cost of equity due to tax shield
        cost_of_equity = self.calculator.calculate_cost_of_equity()
        self.assertLess(wacc, cost_of_equity)
    
    def test_cagr_calculation(self):
        """Test CAGR calculation."""
        values = [100, 110, 121, 133.1]  # 10% annual growth
        cagr = self.calculator._calculate_cagr(values)
        
        # Should be approximately 10%
        self.assertAlmostEqual(cagr, 0.10, places=2)
        
        # Test edge cases
        self.assertEqual(self.calculator._calculate_cagr([100]), 0)
        self.assertEqual(self.calculator._calculate_cagr([]), 0)
    
    def test_fcfe_valuation(self):
        """Test FCFE valuation calculation."""
        result = self.calculator.calculate_fcfe()
        
        self.assertEqual(result['method'], 'FCFE')
        self.assertIn('valuePerShare', result)
        self.assertIn('upside', result)
        self.assertIn('assumptions', result)
        
        # Value per share should be positive for profitable company
        self.assertGreater(result['valuePerShare'], 0)
    
    def test_fcfe_negative_cash_flow(self):
        """Test FCFE valuation with negative cash flow."""
        # Modify data to have negative FCF
        negative_fcf_data = self.mock_data.copy()
        negative_fcf_data['financialHistory']['2024']['freeCashFlow'] = -10000000
        
        calculator = ValuationCalculator(negative_fcf_data)
        result = calculator.calculate_fcfe()
        
        self.assertTrue(result.get('notApplicable'))
        self.assertEqual(result['valuePerShare'], 0)
        self.assertIn('reason', result)
    
    def test_fcff_valuation(self):
        """Test FCFF valuation calculation."""
        result = self.calculator.calculate_fcff()
        
        self.assertEqual(result['method'], 'FCFF')
        self.assertIn('valuePerShare', result)
        self.assertIn('firmValue', result)
        self.assertIn('equityValue', result)
        self.assertIn('upside', result)
        
        # Firm value should be greater than equity value (has debt)
        self.assertGreater(result['firmValue'], result['equityValue'])
    
    def test_ddm_valuation(self):
        """Test Dividend Discount Model calculation."""
        result = self.calculator.calculate_ddm()
        
        self.assertEqual(result['method'], 'DDM (Gordon Growth)')
        self.assertIn('valuePerShare', result)
        self.assertIn('upside', result)
        
        # Should work for dividend-paying company
        self.assertGreater(result['valuePerShare'], 0)
    
    def test_ddm_no_dividend(self):
        """Test DDM with non-dividend paying company."""
        # Modify data to have no dividend
        no_div_data = self.mock_data.copy()
        no_div_data['financialHistory']['2024']['dividend'] = 0
        
        calculator = ValuationCalculator(no_div_data)
        result = calculator.calculate_ddm()
        
        self.assertTrue(result.get('notApplicable'))
        self.assertEqual(result['valuePerShare'], 0)
        self.assertIn('reason', result)
    
    def test_relative_valuation(self):
        """Test relative valuation methods."""
        result = self.calculator.calculate_relative_valuation()
        
        self.assertIn('peValuation', result)
        self.assertIn('pbValuation', result)
        self.assertIn('evEbitdaValuation', result)
        
        # All should have value per share and upside
        for valuation in result.values():
            self.assertIn('valuePerShare', valuation)
            self.assertIn('upside', valuation)
            self.assertGreater(valuation['valuePerShare'], 0)
    
    def test_asset_based_valuation(self):
        """Test asset-based valuation methods."""
        result = self.calculator.calculate_asset_based_valuation()
        
        self.assertIn('bookValue', result)
        self.assertIn('tangibleBookValue', result)
        self.assertIn('liquidationValue', result)
        
        # Book value should match the input data
        book_value_per_share = result['bookValue']['valuePerShare']
        expected_book_value = self.mock_data['financialHistory']['2024']['bookValuePerShare']
        self.assertEqual(book_value_per_share, expected_book_value)
    
    def test_earnings_based_valuation(self):
        """Test earnings-based valuation methods."""
        result = self.calculator.calculate_earnings_based_valuation()
        
        self.assertIn('capitalizedEarnings', result)
        self.assertIn('earningsPowerValue', result)
        
        # Both should have positive values for profitable company
        self.assertGreater(result['capitalizedEarnings']['valuePerShare'], 0)
        self.assertGreater(result['earningsPowerValue']['valuePerShare'], 0)
    
    def test_risk_metrics(self):
        """Test risk metrics calculation."""
        result = self.calculator.calculate_risk_metrics()
        
        self.assertIn('financial', result)
        self.assertIn('business', result)
        self.assertIn('valuation', result)
        
        # Check that risk levels are valid
        financial_risk = result['financial']['riskLevel']
        self.assertIn(financial_risk, ['Low', 'Medium', 'High'])
        
        business_risk = result['business']['volatilityRisk']
        self.assertIn(business_risk, ['Low', 'Medium', 'High'])
    
    def test_dynamic_weights(self):
        """Test dynamic weight calculation."""
        # Get all valuation results first
        fcfe_result = self.calculator.calculate_fcfe()
        fcff_result = self.calculator.calculate_fcff()
        ddm_result = self.calculator.calculate_ddm()
        relative_results = self.calculator.calculate_relative_valuation()
        asset_results = self.calculator.calculate_asset_based_valuation()
        earnings_results = self.calculator.calculate_earnings_based_valuation()
        
        weights = self.calculator.calculate_dynamic_weights(
            fcfe_result, fcff_result, ddm_result,
            relative_results, asset_results, earnings_results
        )
        
        # Weights should sum to 1
        total_weight = sum(weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=6)
        
        # All weights should be non-negative
        for weight in weights.values():
            self.assertGreaterEqual(weight, 0)
    
    def test_confidence_calculation(self):
        """Test confidence level calculation."""
        valuations = [
            {'value': 100, 'weight': 0.3},
            {'value': 105, 'weight': 0.3},
            {'value': 95, 'weight': 0.4}
        ]
        
        confidence = self.calculator.calculate_confidence(valuations)
        self.assertIn(confidence, ['Low', 'Medium', 'High'])
    
    def test_recommendation_logic(self):
        """Test investment recommendation logic."""
        # Test various scenarios
        self.assertEqual(self.calculator.get_recommendation(25, 20), 'Strong Buy')
        self.assertEqual(self.calculator.get_recommendation(15, 12), 'Buy')
        self.assertEqual(self.calculator.get_recommendation(5, 8), 'Hold')
        self.assertEqual(self.calculator.get_recommendation(-5, 2), 'Hold')
        self.assertEqual(self.calculator.get_recommendation(-15, 0), 'Sell')
    
    def test_comprehensive_valuation(self):
        """Test the complete intrinsic value calculation."""
        result = self.calculator.calculate_intrinsic_value()
        
        # Check all required fields are present
        required_fields = [
            'ticker', 'companyName', 'currentPrice', 'intrinsicValue',
            'upside', 'marginOfSafety', 'recommendation', 'confidence',
            'valuationBreakdown', 'weightedValuations', 'weightingRationale',
            'riskMetrics', 'summary'
        ]
        
        for field in required_fields:
            self.assertIn(field, result)
        
        # Check that intrinsic value is reasonable
        self.assertGreater(result['intrinsicValue'], 0)
        self.assertIsInstance(result['upside'], (int, float))
        self.assertIsInstance(result['marginOfSafety'], (int, float))
        
        # Check summary structure
        summary = result['summary']
        summary_fields = ['valuation', 'opportunity', 'risk', 'recommendation']
        for field in summary_fields:
            self.assertIn(field, summary)
            self.assertIsInstance(summary[field], str)


def load_real_data_test():
    """
    Test with real company data if available.
    This is a separate function to avoid test failures if data files don't exist.
    """
    try:
        # Try to load CAT data for real-world testing
        current_dir = Path(__file__).parent
        data_path = current_dir.parent.parent.parent / 'data' / 'cat.json'
        
        if data_path.exists():
            with open(data_path, 'r') as f:
                cat_data = json.load(f)
            
            calculator = ValuationCalculator(cat_data)
            result = calculator.calculate_intrinsic_value()
            
            print(f"\n🧪 Real Data Test Results for {result['ticker']}:")
            print(f"Current Price: ${result['currentPrice']:.2f}")
            print(f"Intrinsic Value: ${result['intrinsicValue']:.2f}")
            print(f"Upside: {result['upside']:.1f}%")
            print(f"Recommendation: {result['recommendation']}")
            print(f"Confidence: {result['confidence']}")
            
            return True
        else:
            print(f"\n⚠️  CAT data file not found at {data_path}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing with real data: {e}")
        return False


if __name__ == '__main__':
    # Run the unit tests
    print("🧪 Running Python ValuationCalculator Tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run real data test if available
    print("\n" + "="*60)
    load_real_data_test()
