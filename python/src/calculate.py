#!/usr/bin/env python3
"""
Company Value Calculator - Command Line Interface

This script provides a command-line interface for calculating intrinsic values
of companies using comprehensive valuation methodologies.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

from data.data_loader import DataLoader
from models.company_data import CompanyData
from valuation_calculator_modular import ValuationCalculator
from output.cli_printer import CLIPrinter


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
    parser.add_argument('--raw-assumptions', action='store_true',
                       help='Use original data assumptions (disable standardization)')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate standardization framework report')
    
    args = parser.parse_args()
    
    # Determine whether to use standardized assumptions
    use_standardized_assumptions = not args.raw_assumptions
    
    # Initialize data loader
    data_loader = DataLoader(DataLoader.get_default_data_directory(), use_standardized_assumptions)
    
    if args.list:
        companies = data_loader.list_available_companies()
        CLIPrinter.list_available_companies(companies)
        return
    
    try:
        ticker = args.ticker.upper()
        CLIPrinter.print_loading_message(ticker)
        
        # Print standardization status
        if use_standardized_assumptions:
            print("🎯 Using Standardized Assumption Framework for consistent valuations")
        else:
            print("📊 Using original data assumptions (raw mode)")
        
        # Load and validate company data
        company_data = data_loader.load_company_data(ticker)
        
        # Generate standardization report if requested
        if args.generate_report and use_standardized_assumptions:
            from data.standardized_assumptions import create_standardized_framework
            framework = create_standardized_framework()
            report = framework.generate_assumption_report(company_data.raw_data)
            
            output_dir = Path(__file__).parent / args.output_dir
            output_dir.mkdir(exist_ok=True)
            
            date_str = datetime.now().strftime('%Y-%m-%d')
            report_path = output_dir / f'{ticker.lower()}_assumptions_report_{date_str}.txt'
            
            with open(report_path, 'w') as f:
                f.write(report)
            
            print(f"📊 Standardization report saved to: {report_path}")
        
        # Calculate intrinsic value using modular calculator
        calculator = ValuationCalculator(company_data)
        results = calculator.calculate_intrinsic_value()
        
        # Print results
        CLIPrinter.print_valuation_results(results, company_data)
        
        # Optional: Save results to file
        if args.save:
            output_dir = Path(__file__).parent / args.output_dir
            output_dir.mkdir(exist_ok=True)
            
            date_str = datetime.now().strftime('%Y-%m-%d')
            output_path = output_dir / f'{ticker.lower()}_valuation_{date_str}.json'
            
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n📁 Detailed results saved to: {output_path}")
    
    except FileNotFoundError as e:
        CLIPrinter.print_error(str(e))
        print(f"\n💡 Available company data files:")
        
        companies = data_loader.list_available_companies()
        if companies:
            for company in companies:
                print(f"   - {company['ticker']}")
            print(f"\nUsage: python calculate.py <TICKER>")
            print(f"Example: python calculate.py CAT")
        else:
            print(f"   No company data files found in data directory")
    
    except json.JSONDecodeError as e:
        CLIPrinter.print_error(f"Invalid JSON in company data file - {e}")
    
    except Exception as e:
        CLIPrinter.print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
