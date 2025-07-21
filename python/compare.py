#!/usr/bin/env python3
"""
Comparison utility to verify Python implementation matches JavaScript results.

This script runs both implementations and compares the key metrics to ensure
the Python port is accurate.
"""

import subprocess
import json
import sys
from pathlib import Path


def run_javascript_calculation(ticker: str) -> dict:
    """Run the JavaScript implementation and parse results."""
    try:
        # Change to the parent directory and run JavaScript version
        parent_dir = Path(__file__).parent.parent
        result = subprocess.run(
            ['node', 'src/calculate.js', ticker],
            cwd=parent_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"JavaScript error: {result.stderr}")
            return None
            
        # Look for the saved JSON file
        output_dir = parent_dir / 'output'
        json_files = list(output_dir.glob(f'{ticker.lower()}_valuation_*.json'))
        
        if json_files:
            # Get the most recent file
            latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            with open(latest_file, 'r') as f:
                return json.load(f)
        
        return None
        
    except Exception as e:
        print(f"Error running JavaScript version: {e}")
        return None


def run_python_calculation(ticker: str) -> dict:
    """Run the Python implementation and return results."""
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        from valuation_calculator import ValuationCalculator
        
        # Load company data
        data_path = Path(__file__).parent.parent / 'data' / f'{ticker.lower()}.json'
        with open(data_path, 'r') as f:
            company_data = json.load(f)
        
        calculator = ValuationCalculator(company_data)
        return calculator.calculate_intrinsic_value()
        
    except Exception as e:
        print(f"Error running Python version: {e}")
        return None


def compare_results(js_result: dict, py_result: dict, ticker: str) -> None:
    """Compare the results from both implementations."""
    print(f"\n📊 COMPARISON RESULTS FOR {ticker}")
    print("=" * 60)
    
    if not js_result or not py_result:
        print("❌ One or both calculations failed")
        return
    
    # Key metrics to compare
    metrics = [
        ('currentPrice', 'Current Price'),
        ('intrinsicValue', 'Intrinsic Value'),
        ('upside', 'Upside %'),
        ('marginOfSafety', 'Margin of Safety %'),
        ('recommendation', 'Recommendation'),
        ('confidence', 'Confidence')
    ]
    
    print(f"{'Metric':<20} {'JavaScript':<15} {'Python':<15} {'Match':<8}")
    print("-" * 60)
    
    all_match = True
    
    for key, name in metrics:
        js_val = js_result.get(key)
        py_val = py_result.get(key)
        
        if isinstance(js_val, (int, float)) and isinstance(py_val, (int, float)):
            # For numeric values, check if they're close (within 0.01%)
            match = abs(js_val - py_val) < abs(js_val * 0.0001) if js_val != 0 else py_val == 0
            js_str = f"{js_val:.2f}"
            py_str = f"{py_val:.2f}"
        else:
            # For string values, exact match
            match = js_val == py_val
            js_str = str(js_val)
            py_str = str(py_val)
        
        match_str = "✅" if match else "❌"
        if not match:
            all_match = False
        
        print(f"{name:<20} {js_str:<15} {py_str:<15} {match_str:<8}")
    
    print("-" * 60)
    
    if all_match:
        print("🎉 All key metrics match! Python implementation is accurate.")
    else:
        print("⚠️  Some metrics differ. This may be due to rounding or implementation details.")
    
    # Compare individual valuation methods
    print(f"\n📈 VALUATION METHOD COMPARISON:")
    print("-" * 60)
    
    js_breakdown = js_result.get('valuationBreakdown', {})
    py_breakdown = py_result.get('valuationBreakdown', {})
    
    methods = [
        ('fcfe', 'FCFE'),
        ('fcff', 'FCFF'),
        ('ddm', 'DDM'),
    ]
    
    for key, name in methods:
        js_method = js_breakdown.get(key, {})
        py_method = py_breakdown.get(key, {})
        
        js_value = js_method.get('valuePerShare', 0)
        py_value = py_method.get('valuePerShare', 0)
        
        if isinstance(js_value, (int, float)) and isinstance(py_value, (int, float)):
            match = abs(js_value - py_value) < abs(js_value * 0.0001) if js_value != 0 else py_value == 0
            match_str = "✅" if match else "❌"
            print(f"{name:<20} ${js_value:<14.2f} ${py_value:<14.2f} {match_str}")


def main():
    """Main comparison function."""
    if len(sys.argv) < 2:
        ticker = 'CAT'
    else:
        ticker = sys.argv[1].upper()
    
    print(f"🔍 Comparing JavaScript vs Python implementations for {ticker}")
    print("This may take a moment...")
    
    # Run both implementations
    print("\n⏳ Running JavaScript implementation...")
    js_result = run_javascript_calculation(ticker)
    
    print("⏳ Running Python implementation...")
    py_result = run_python_calculation(ticker)
    
    # Compare results
    compare_results(js_result, py_result, ticker)


if __name__ == '__main__':
    main()
