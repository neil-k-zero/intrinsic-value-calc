#!/usr/bin/env python3
"""
Financial Data Calculator for Company Valuation Data Files

This script helps calculate financial metrics, ratios, and statistics that may not be
directly available from stock analysis websites like stockanalysis.com. It's designed
to complement the data gathering process for creating comprehensive company data files.

Usage:
    python data_calculator.py --help
    python data_calculator.py --calculate-ratios --revenue 100000 --net-income 15000 --total-assets 200000
    python data_calculator.py --validate-data /path/to/company.json
    python data_calculator.py --currency-convert --amount 1000 --from DKK --to USD --rate 0.145
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialCalculator:
    """
    Calculator for financial metrics and ratios not readily available from external sources.
    """
    
    # Common exchange rates (as of July 2025)
    EXCHANGE_RATES = {
        'DKK_TO_USD': 0.145,
        'EUR_TO_USD': 1.09,
        'GBP_TO_USD': 1.27,
        'CAD_TO_USD': 0.73,
        'JPY_TO_USD': 0.0067,
        'CHF_TO_USD': 1.12
    }
    
    def __init__(self):
        self.precision = 4
    
    def calculate_growth_rates(self, values: List[float], periods: Optional[int] = None) -> Dict[str, float]:
        """
        Calculate various growth rates from a list of values.
        
        Args:
            values: List of financial values (oldest to newest)
            periods: Number of periods (defaults to len(values) - 1)
            
        Returns:
            Dictionary with growth rate calculations
        """
        if len(values) < 2:
            return {'error': 'Need at least 2 values for growth calculation'}
        
        results = {}
        
        # Year-over-year growth
        yoy_growth = ((values[-1] / values[-2]) - 1) if values[-2] != 0 else 0
        results['yoy_growth'] = round(yoy_growth, self.precision)
        
        # CAGR (Compound Annual Growth Rate)
        if len(values) >= 2:
            years = len(values) - 1 if periods is None else periods
            if years > 0 and values[0] > 0:
                cagr = (values[-1] / values[0]) ** (1 / years) - 1
                results['cagr'] = round(cagr, self.precision)
        
        # Average annual growth
        if len(values) >= 3:
            annual_growths = []
            for i in range(1, len(values)):
                if values[i-1] > 0:
                    growth = (values[i] / values[i-1]) - 1
                    annual_growths.append(growth)
            
            if annual_growths:
                avg_growth = sum(annual_growths) / len(annual_growths)
                results['average_growth'] = round(avg_growth, self.precision)
        
        return results
    
    def calculate_financial_ratios(self, financial_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate comprehensive financial ratios from basic financial statement data.
        
        Args:
            financial_data: Dictionary with financial statement items
            
        Returns:
            Dictionary with calculated ratios
        """
        ratios = {}
        
        # Extract basic data
        revenue = financial_data.get('revenue', 0)
        gross_profit = financial_data.get('gross_profit', 0)
        operating_income = financial_data.get('operating_income', 0)
        net_income = financial_data.get('net_income', 0)
        total_assets = financial_data.get('total_assets', 0)
        total_debt = financial_data.get('total_debt', 0)
        shareholders_equity = financial_data.get('shareholders_equity', 0)
        current_assets = financial_data.get('current_assets', 0)
        current_liabilities = financial_data.get('current_liabilities', 0)
        cash = financial_data.get('cash', 0)
        inventory = financial_data.get('inventory', 0)
        accounts_receivable = financial_data.get('accounts_receivable', 0)
        
        # Profitability Ratios
        if revenue > 0:
            ratios['gross_margin'] = round(gross_profit / revenue, self.precision)
            ratios['operating_margin'] = round(operating_income / revenue, self.precision)
            ratios['net_margin'] = round(net_income / revenue, self.precision)
        
        if total_assets > 0:
            ratios['roa'] = round(net_income / total_assets, self.precision)
            ratios['asset_turnover'] = round(revenue / total_assets, self.precision)
        
        if shareholders_equity > 0:
            ratios['roe'] = round(net_income / shareholders_equity, self.precision)
        
        # Liquidity Ratios
        if current_liabilities > 0:
            ratios['current_ratio'] = round(current_assets / current_liabilities, self.precision)
            quick_assets = current_assets - inventory
            ratios['quick_ratio'] = round(quick_assets / current_liabilities, self.precision)
            ratios['cash_ratio'] = round(cash / current_liabilities, self.precision)
        
        # Leverage Ratios
        if shareholders_equity > 0:
            ratios['debt_to_equity'] = round(total_debt / shareholders_equity, self.precision)
        
        if total_assets > 0:
            ratios['debt_to_assets'] = round(total_debt / total_assets, self.precision)
        
        # Efficiency Ratios
        if revenue > 0:
            if inventory > 0:
                # Assume COGS = Revenue - Gross Profit
                cogs = revenue - gross_profit
                ratios['inventory_turnover'] = round(cogs / inventory, self.precision)
            
            if accounts_receivable > 0:
                ratios['receivables_turnover'] = round(revenue / accounts_receivable, self.precision)
        
        return ratios
    
    def calculate_valuation_metrics(self, market_data: Dict[str, float], financial_data: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate valuation metrics from market and financial data.
        
        Args:
            market_data: Market-related data (price, shares, market cap)
            financial_data: Financial statement data
            
        Returns:
            Dictionary with valuation metrics
        """
        metrics = {}
        
        # Extract data
        current_price = market_data.get('current_price', 0)
        shares_outstanding = market_data.get('shares_outstanding', 0)
        market_cap = market_data.get('market_cap', 0)
        
        revenue = financial_data.get('revenue', 0)
        net_income = financial_data.get('net_income', 0)
        book_value = financial_data.get('shareholders_equity', 0)
        free_cash_flow = financial_data.get('free_cash_flow', 0)
        
        if shares_outstanding > 0:
            eps = net_income / shares_outstanding
            book_value_per_share = book_value / shares_outstanding
            fcf_per_share = free_cash_flow / shares_outstanding
            
            if current_price > 0:
                if eps > 0:
                    metrics['pe_ratio'] = round(current_price / eps, self.precision)
                if book_value_per_share > 0:
                    metrics['pb_ratio'] = round(current_price / book_value_per_share, self.precision)
                if fcf_per_share > 0:
                    metrics['price_to_fcf'] = round(current_price / fcf_per_share, self.precision)
        
        if market_cap > 0 and revenue > 0:
            metrics['ps_ratio'] = round(market_cap / revenue, self.precision)
        
        return metrics
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str, 
                        exchange_rate: Optional[float] = None) -> Dict[str, Any]:
        """
        Convert currency amounts with proper exchange rates.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            exchange_rate: Custom exchange rate (optional)
            
        Returns:
            Dictionary with conversion results
        """
        if from_currency == to_currency:
            return {'converted_amount': amount, 'rate_used': 1.0, 'note': 'Same currency'}
        
        # Use custom rate if provided
        if exchange_rate:
            converted = amount * exchange_rate
            return {
                'converted_amount': round(converted, 2),
                'rate_used': exchange_rate,
                'note': f'Custom rate: 1 {from_currency} = {exchange_rate} {to_currency}'
            }
        
        # Use predefined rates
        rate_key = f'{from_currency}_TO_{to_currency}'
        if rate_key in self.EXCHANGE_RATES:
            rate = self.EXCHANGE_RATES[rate_key]
            converted = amount * rate
            return {
                'converted_amount': round(converted, 2),
                'rate_used': rate,
                'note': f'Standard rate: 1 {from_currency} = {rate} {to_currency}'
            }
        
        return {'error': f'Exchange rate not available for {from_currency} to {to_currency}'}
    
    def estimate_missing_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate missing financial metrics using available data and industry standards.
        
        Args:
            data: Partial financial data
            
        Returns:
            Dictionary with estimated values
        """
        estimates = {}
        
        # Estimate EBITDA if missing
        if 'operating_income' in data and 'ebitda' not in data:
            # Typical D&A is 3-8% of revenue for most industries
            operating_income = data['operating_income']
            revenue = data.get('revenue', 0)
            
            if revenue > 0:
                # Conservative estimate: 5% of revenue for D&A
                estimated_da = revenue * 0.05
                estimated_ebitda = operating_income + estimated_da
                estimates['estimated_ebitda'] = round(estimated_ebitda, 0)
                estimates['ebitda_note'] = 'Estimated using Operating Income + 5% of revenue for D&A'
        
        # Estimate Free Cash Flow if missing
        if 'operating_cash_flow' in data and 'capex' in data and 'free_cash_flow' not in data:
            ocf = data['operating_cash_flow']
            capex = data['capex']
            estimated_fcf = ocf - capex
            estimates['estimated_free_cash_flow'] = round(estimated_fcf, 0)
            estimates['fcf_note'] = 'Calculated as Operating Cash Flow - Capital Expenditures'
        
        # Estimate Working Capital if missing
        if all(k in data for k in ['current_assets', 'current_liabilities']) and 'working_capital' not in data:
            wc = data['current_assets'] - data['current_liabilities']
            estimates['estimated_working_capital'] = round(wc, 0)
            estimates['wc_note'] = 'Calculated as Current Assets - Current Liabilities'
        
        # Estimate Interest Coverage if missing
        if 'operating_income' in data and 'interest_expense' in data and 'interest_coverage' not in data:
            if data['interest_expense'] > 0:
                coverage = data['operating_income'] / data['interest_expense']
                estimates['estimated_interest_coverage'] = round(coverage, 2)
                estimates['interest_coverage_note'] = 'Calculated as Operating Income / Interest Expense'
        
        return estimates


class DataValidator:
    """
    Validates company data files for completeness and accuracy.
    """
    
    REQUIRED_FIELDS = {
        'ticker', 'companyName', 'industry', 'sector', 'lastUpdated',
        'marketData', 'financialHistory', 'keyRatios'
    }
    
    MARKET_DATA_FIELDS = {
        'currentPrice', 'marketCap', 'sharesOutstanding', 'beta'
    }
    
    FINANCIAL_FIELDS = {
        'revenue', 'netIncome', 'totalAssets', 'totalDebt', 'shareholdersEquity'
    }
    
    def validate_data_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a company data JSON file for completeness.
        
        Args:
            file_path: Path to the JSON data file
            
        Returns:
            Validation report
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            return {'error': f'Failed to load file: {str(e)}'}
        
        report = {
            'file_path': file_path,
            'validation_passed': True,
            'missing_fields': [],
            'warnings': [],
            'data_quality_score': 0
        }
        
        # Check required top-level fields
        missing_top_level = self.REQUIRED_FIELDS - set(data.keys())
        if missing_top_level:
            report['missing_fields'].extend(list(missing_top_level))
            report['validation_passed'] = False
        
        # Check market data
        if 'marketData' in data:
            missing_market = self.MARKET_DATA_FIELDS - set(data['marketData'].keys())
            if missing_market:
                report['warnings'].append(f'Missing market data fields: {list(missing_market)}')
        
        # Check financial history
        if 'financialHistory' in data:
            years_available = len(data['financialHistory'])
            if years_available < 3:
                report['warnings'].append(f'Limited financial history: only {years_available} years')
            
            # Check latest year data
            latest_year = max(data['financialHistory'].keys())
            latest_data = data['financialHistory'][latest_year]
            missing_financial = self.FINANCIAL_FIELDS - set(latest_data.keys())
            if missing_financial:
                report['warnings'].append(f'Missing financial fields in {latest_year}: {list(missing_financial)}')
        
        # Calculate data quality score
        total_possible_points = 100
        deductions = 0
        
        deductions += len(report['missing_fields']) * 20  # 20 points per missing required field
        deductions += len(report['warnings']) * 5         # 5 points per warning
        
        report['data_quality_score'] = max(0, total_possible_points - deductions)
        
        return report


def main():
    """Main CLI interface for the financial calculator."""
    parser = argparse.ArgumentParser(
        description='Financial Data Calculator for Company Valuation Files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calculate financial ratios
  python data_calculator.py --calculate-ratios --revenue 100000000 --net-income 15000000 --total-assets 200000000
  
  # Convert currency
  python data_calculator.py --currency-convert --amount 1000 --from DKK --to USD --rate 0.145
  
  # Validate data file
  python data_calculator.py --validate-data data/nvo.json
  
  # Calculate growth rates
  python data_calculator.py --growth-rates --values 100,120,150,180
        """
    )
    
    # Subcommand groups
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Financial ratios calculator
    ratios_parser = subparsers.add_parser('ratios', help='Calculate financial ratios')
    ratios_parser.add_argument('--revenue', type=float, required=True, help='Revenue')
    ratios_parser.add_argument('--gross-profit', type=float, help='Gross profit')
    ratios_parser.add_argument('--operating-income', type=float, help='Operating income')
    ratios_parser.add_argument('--net-income', type=float, required=True, help='Net income')
    ratios_parser.add_argument('--total-assets', type=float, required=True, help='Total assets')
    ratios_parser.add_argument('--total-debt', type=float, help='Total debt')
    ratios_parser.add_argument('--shareholders-equity', type=float, help='Shareholders equity')
    ratios_parser.add_argument('--current-assets', type=float, help='Current assets')
    ratios_parser.add_argument('--current-liabilities', type=float, help='Current liabilities')
    
    # Currency converter
    currency_parser = subparsers.add_parser('convert', help='Convert currency amounts')
    currency_parser.add_argument('--amount', type=float, required=True, help='Amount to convert')
    currency_parser.add_argument('--from', dest='from_currency', required=True, help='Source currency')
    currency_parser.add_argument('--to', dest='to_currency', required=True, help='Target currency')
    currency_parser.add_argument('--rate', type=float, help='Custom exchange rate')
    
    # Data validator
    validator_parser = subparsers.add_parser('validate', help='Validate company data file')
    validator_parser.add_argument('file_path', help='Path to JSON data file')
    
    # Growth rates calculator
    growth_parser = subparsers.add_parser('growth', help='Calculate growth rates')
    growth_parser.add_argument('--values', required=True, help='Comma-separated values (oldest to newest)')
    growth_parser.add_argument('--periods', type=int, help='Number of periods')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    calculator = FinancialCalculator()
    validator = DataValidator()
    
    try:
        if args.command == 'ratios':
            financial_data = {
                'revenue': args.revenue,
                'gross_profit': args.gross_profit or 0,
                'operating_income': args.operating_income or 0,
                'net_income': args.net_income,
                'total_assets': args.total_assets,
                'total_debt': args.total_debt or 0,
                'shareholders_equity': args.shareholders_equity or 0,
                'current_assets': args.current_assets or 0,
                'current_liabilities': args.current_liabilities or 0
            }
            
            ratios = calculator.calculate_financial_ratios(financial_data)
            print("\n📊 CALCULATED FINANCIAL RATIOS")
            print("=" * 50)
            for ratio_name, value in ratios.items():
                print(f"{ratio_name.replace('_', ' ').title()}: {value}")
        
        elif args.command == 'convert':
            result = calculator.convert_currency(
                args.amount, 
                args.from_currency, 
                args.to_currency, 
                args.rate
            )
            
            print("\n💱 CURRENCY CONVERSION")
            print("=" * 30)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Original Amount: {args.amount:,.2f} {args.from_currency}")
                print(f"Converted Amount: {result['converted_amount']:,.2f} {args.to_currency}")
                print(f"Exchange Rate: {result['rate_used']}")
                print(f"Note: {result['note']}")
        
        elif args.command == 'validate':
            report = validator.validate_data_file(args.file_path)
            
            print("\n🔍 DATA VALIDATION REPORT")
            print("=" * 40)
            print(f"File: {report['file_path']}")
            print(f"Validation Passed: {report['validation_passed']}")
            print(f"Data Quality Score: {report['data_quality_score']}/100")
            
            if report['missing_fields']:
                print(f"\n❌ Missing Required Fields:")
                for field in report['missing_fields']:
                    print(f"  - {field}")
            
            if report['warnings']:
                print(f"\n⚠️  Warnings:")
                for warning in report['warnings']:
                    print(f"  - {warning}")
            
            if report['validation_passed'] and not report['warnings']:
                print("\n✅ Data file is complete and well-structured!")
        
        elif args.command == 'growth':
            values = [float(x.strip()) for x in args.values.split(',')]
            growth_rates = calculator.calculate_growth_rates(values, args.periods)
            
            print("\n📈 GROWTH RATE ANALYSIS")
            print("=" * 35)
            for rate_name, value in growth_rates.items():
                if rate_name != 'error':
                    print(f"{rate_name.replace('_', ' ').title()}: {value:.2%}")
                else:
                    print(f"Error: {value}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
