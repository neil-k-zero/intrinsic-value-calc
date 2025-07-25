#!/usr/bin/env python3
"""
Company Value Calculator - Command Line Interface

This script provides a command-line interface for calculating intrinsic values
of companies using multiple valuation methods.

IMPORTANT: This is the original monolithic implementation. 
For the new modular design, see calculate_modular.py and the modular/ directory.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

from valuation_calculator import ValuationCalculator


def load_company_data(ticker: str) -> Dict[str, Any]:
    """
    Load company data from JSON file.
    
    Args:
        ticker: Company ticker symbol
        
    Returns:
        Company data dictionary
        
    Raises:
        FileNotFoundError: If company data file doesn't exist
        json.JSONDecodeError: If JSON file is invalid
    """
    # Get the parent directory of the current script to find data folder
    current_dir = Path(__file__).parent
    data_path = current_dir.parent.parent / 'data' / f'{ticker.lower()}.json'
    
    if not data_path.exists():
        raise FileNotFoundError(f"Company data file not found: {data_path}")
    
    with open(data_path, 'r') as file:
        return json.load(file)


def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format currency amount for display.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == 'DKK':
        return f"DKK {amount:,.2f}"
    else:
        return f"${amount:,.2f}"


def format_percent(value: float, decimals: int = 1) -> str:
    """
    Format percentage for display.
    
    Args:
        value: Percentage value
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


def print_divider(title: str = '') -> None:
    """
    Print a divider line with optional title.
    
    Args:
        title: Optional title to include in divider
    """
    divider = '=' * 80
    if title:
        padding = max(0, (80 - len(title) - 2) // 2)
        print(divider)
        print(' ' * padding + title + ' ' * (80 - len(title) - padding))
    print(divider)


def print_valuation_results(results: Dict[str, Any], company_data: Dict[str, Any]) -> None:
    """
    Print comprehensive valuation results to console.
    
    Args:
        results: Valuation results dictionary
        company_data: Original company data
    """
    # Get currency information from company data
    base_currency = company_data.get('currency', 'USD')
    display_currency = company_data.get('marketData', {}).get('currentPriceCurrency', 'USD')
    
    print('\n')
    print_divider(f"INTRINSIC VALUE ANALYSIS: {results['companyName']} ({results['ticker']})")
    
    # Display currency information if different from USD
    if base_currency != 'USD' or display_currency != 'USD':
        print(f"\n💱 CURRENCY INFORMATION:")
        print(f"Financial Data Currency: {base_currency}")
        print(f"Stock Price Currency: {display_currency}")
        if company_data.get('currencyNote'):
            print(f"Note: {company_data['currencyNote']}")
    
    print(f"\n📊 EXECUTIVE SUMMARY")
    print(f"Current Price:     {format_currency(results['currentPrice'], display_currency)}")
    print(f"Intrinsic Value:   {format_currency(results['intrinsicValue'], display_currency)}")
    print(f"Potential Upside:  {format_percent(results['upside'])}")
    print(f"Margin of Safety:  {format_percent(results['marginOfSafety'])}")
    print(f"Recommendation:    {results['recommendation']}")
    print(f"Confidence Level:  {results['confidence']}")
    
    print(f"\n🔍 DETAILED VALUATION BREAKDOWN")
    print(f"\n1. DISCOUNTED CASH FLOW MODELS:")
    
    # FCFE Analysis
    fcfe = results['valuationBreakdown']['fcfe']
    print(f"   Free Cash Flow to Equity (FCFE):")
    if fcfe.get('notApplicable'):
        print(f"   └─ Value per Share: N/A")
        print(f"   └─ Reason: {fcfe['reason']}")
        print(f"   └─ Discount Rate: {format_percent(fcfe['assumptions']['discountRate'] * 100)}")
        print(f"   └─ Growth Rate: N/A")
    else:
        print(f"   └─ Value per Share: {format_currency(fcfe['valuePerShare'], display_currency)}")
        print(f"   └─ Upside: {format_percent(fcfe['upside'])}")
        print(f"   └─ Discount Rate: {format_percent(fcfe['assumptions']['discountRate'] * 100)}")
        print(f"   └─ Growth Rate: {format_percent(fcfe['assumptions']['initialGrowth'] * 100)}")
    
    # FCFF Analysis
    fcff = results['valuationBreakdown']['fcff']
    print(f"\n   Free Cash Flow to Firm (FCFF):")
    print(f"   └─ Value per Share: {format_currency(fcff['valuePerShare'], display_currency)}")
    print(f"   └─ Upside: {format_percent(fcff['upside'])}")
    print(f"   └─ WACC: {format_percent(fcff['assumptions']['wacc'] * 100)}")
    print(f"   └─ Net Debt: {format_currency(fcff['assumptions']['netDebt'] / 1000000, 'USD')}M")
    
    # DDM Analysis
    ddm = results['valuationBreakdown']['ddm']
    print(f"\n   Dividend Discount Model:")
    if ddm.get('notApplicable'):
        print(f"   └─ Value per Share: N/A")
        print(f"   └─ Reason: {ddm['reason']}")
    else:
        print(f"   └─ Value per Share: {format_currency(ddm['valuePerShare'], display_currency)}")
        print(f"   └─ Upside: {format_percent(ddm['upside'])}")
        print(f"   └─ Current Dividend: {format_currency(ddm['assumptions']['currentDividend'], 'USD')}")
        print(f"   └─ Growth Rate: {format_percent(ddm['assumptions']['dividendGrowthRate'] * 100)}")
    
    print(f"\n2. RELATIVE VALUATION:")
    relative = results['valuationBreakdown']['relative']
    
    print(f"   P/E Ratio Analysis:")
    print(f"   └─ Value per Share: {format_currency(relative['peValuation']['valuePerShare'], display_currency)}")
    print(f"   └─ Current P/E: {relative['peValuation']['currentPE']:.1f}x")
    print(f"   └─ Fair P/E: {relative['peValuation']['fairPE']:.1f}x")
    print(f"   └─ Upside: {format_percent(relative['peValuation']['upside'])}")
    
    print(f"\n   EV/EBITDA Analysis:")
    print(f"   └─ Value per Share: {format_currency(relative['evEbitdaValuation']['valuePerShare'], display_currency)}")
    print(f"   └─ Current Multiple: {relative['evEbitdaValuation']['currentMultiple']:.1f}x")
    print(f"   └─ Fair Multiple: {relative['evEbitdaValuation']['fairMultiple']:.1f}x")
    print(f"   └─ Upside: {format_percent(relative['evEbitdaValuation']['upside'])}")
    
    print(f"\n3. ASSET-BASED VALUATION:")
    asset = results['valuationBreakdown']['assetBased']
    
    print(f"   Book Value: {format_currency(asset['bookValue']['valuePerShare'], display_currency)} ({format_percent(asset['bookValue']['upside'])} upside)")
    print(f"   Tangible Book Value: {format_currency(asset['tangibleBookValue']['valuePerShare'], display_currency)} ({format_percent(asset['tangibleBookValue']['upside'])} upside)")
    print(f"   Liquidation Value: {format_currency(asset['liquidationValue']['valuePerShare'], display_currency)} ({format_percent(asset['liquidationValue']['upside'])} upside)")
    
    print(f"\n4. EARNINGS-BASED VALUATION:")
    earnings = results['valuationBreakdown']['earningsBased']
    
    print(f"   Capitalized Earnings: {format_currency(earnings['capitalizedEarnings']['valuePerShare'], display_currency)} ({format_percent(earnings['capitalizedEarnings']['upside'])} upside)")
    print(f"   Earnings Power Value: {format_currency(earnings['earningsPowerValue']['valuePerShare'], display_currency)} ({format_percent(earnings['earningsPowerValue']['upside'])} upside)")
    
    print(f"\n📈 WEIGHTED VALUATION SUMMARY")
    for val in results['weightedValuations']:
        method_name = val['method'].ljust(35)
        value_str = format_currency(val['value'], display_currency).rjust(12)
        weight_str = format_percent(val['weight'] * 100, 0)
        print(f"   {method_name} {value_str} ({weight_str} weight)")
    
    print(f"\n⚠️  RISK ASSESSMENT")
    risk = results['riskMetrics']
    print(f"Financial Risk:    {risk['financial']['riskLevel']}")
    
    # Handle null values gracefully
    debt_to_equity = risk['financial']['debtToEquity']
    current_ratio = risk['financial']['currentRatio']
    interest_coverage = risk['financial']['interestCoverage']
    beta = risk['business']['beta']
    pe_ratio = risk['valuation']['peRatio']
    pb_ratio = risk['valuation']['pbRatio']
    
    debt_str = f"{debt_to_equity:.2f}x" if debt_to_equity is not None else "N/A (Negative Equity)"
    current_str = f"{current_ratio:.2f}x" if current_ratio is not None else "N/A"
    interest_str = f"{interest_coverage:.1f}x" if interest_coverage is not None else "N/A"
    
    print(f"└─ Debt/Equity:    {debt_str}")
    print(f"└─ Current Ratio:  {current_str}")
    print(f"└─ Interest Cover: {interest_str}")
    
    print(f"\nBusiness Risk:     {risk['business']['volatilityRisk']}")
    print(f"└─ Beta:           {beta:.2f}")
    print(f"└─ Industry:       {risk['business']['industryRisk']}")
    
    print(f"\nValuation Risk:    {risk['valuation']['valuationRisk']}")
    pe_str = f"{pe_ratio:.1f}x" if pe_ratio is not None else "N/A"
    pb_str = f"{pb_ratio:.1f}x" if pb_ratio is not None else "N/A"
    print(f"└─ P/E Ratio:      {pe_str}")
    print(f"└─ P/B Ratio:      {pb_str}")
    
    print(f"\n💡 INVESTMENT SUMMARY")
    print(f"{results['summary']['valuation']}")
    print(f"{results['summary']['opportunity']}")
    print(f"{results['summary']['risk']}")
    print(f"{results['summary']['recommendation']}")
    
    print_divider()
    print(f"\n⚠️  IMPORTANT DISCLAIMER:")
    print(f"This analysis is for educational purposes only and does not constitute")
    print(f"investment advice. Always consult with qualified financial professionals")
    print(f"and conduct your own research before making investment decisions.")
    print_divider()


def list_available_companies() -> None:
    """List all available company data files."""
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent.parent / 'data'
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    json_files = list(data_dir.glob('*.json'))
    json_files = [f for f in json_files if f.name != 'template.json']
    
    if not json_files:
        print(f"No company data files found in {data_dir}")
        return
    
    print(f"\n📋 Available Companies ({len(json_files)}):")
    print('=' * 80)
    
    for file_path in sorted(json_files):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            ticker = data.get('ticker', 'N/A')
            name = data.get('companyName', 'N/A')
            sector = data.get('sector', 'N/A')
            print(f"{ticker.ljust(6)} | {name[:30].ljust(30)} | {sector}")
        except (json.JSONDecodeError, KeyError):
            print(f"ERROR  | {file_path.stem.upper()[:6].ljust(6)} | Invalid data file")


def main() -> None:
    """Main entry point for the command line interface."""
    parser = argparse.ArgumentParser(
        description='Calculate intrinsic value of companies using multiple valuation methods',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python calculate.py CAT          # Calculate Caterpillar valuation
  python calculate.py --list       # List available companies
  python calculate.py AAPL --save  # Calculate and save Apple valuation
        '''
    )
    
    parser.add_argument('ticker', nargs='?', default='CAT',
                       help='Company ticker symbol (default: CAT)')
    parser.add_argument('--list', action='store_true',
                       help='List all available companies')
    parser.add_argument('--save', action='store_true',
                       help='Save results to output file')
    parser.add_argument('--output-dir', default='../output',
                       help='Output directory for saved results')
    
    args = parser.parse_args()
    
    if args.list:
        list_available_companies()
        return
    
    try:
        ticker = args.ticker.upper()
        print(f"Loading data for {ticker}...")
        company_data = load_company_data(ticker)
        
        print(f"Calculating intrinsic value using multiple valuation methods...")
        calculator = ValuationCalculator(company_data)
        results = calculator.calculate_intrinsic_value()
        
        print_valuation_results(results, company_data)
        
        # Optional: Save results to file
        if args.save:
            output_dir = Path(__file__).parent / args.output_dir
            output_dir.mkdir(exist_ok=True)
            
            from datetime import datetime
            date_str = datetime.now().strftime('%Y-%m-%d')
            output_path = output_dir / f'{ticker.lower()}_valuation_{date_str}.json'
            
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n📁 Detailed results saved to: {output_path}")
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Available company data files:")
        
        current_dir = Path(__file__).parent
        data_dir = current_dir.parent.parent / 'data'
        if data_dir.exists():
            json_files = [f.stem.upper() for f in data_dir.glob('*.json') if f.name != 'template.json']
            if json_files:
                for file in sorted(json_files):
                    print(f"   - {file}")
                print(f"\nUsage: python calculate.py <TICKER>")
                print(f"Example: python calculate.py CAT")
            else:
                print(f"   No company data files found in {data_dir}")
    
    except json.JSONDecodeError as e:
        print(f"\n❌ Error: Invalid JSON in company data file - {e}")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
