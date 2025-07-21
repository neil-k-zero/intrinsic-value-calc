# Company Value Calculator - Python Implementation

A comprehensive intrinsic value calculator that implements multiple professional valuation methodologies with industry-specific weighting to determine the fair value of publicly traded companies.

## Features

### Valuation Methods
- **Discounted Cash Flow (DCF)**
  - Free Cash Flow to Equity (FCFE) with multi-stage growth
  - Free Cash Flow to Firm (FCFF) with WACC discounting
- **Dividend Discount Model (DDM)**
  - Gordon Growth Model for dividend-paying stocks
- **Relative Valuation**
  - P/E ratio analysis with industry benchmarks
  - EV/EBITDA multiple analysis
  - **EV/Sales analysis** (crucial for growth companies)
- **Asset-Based Valuation**
  - Book value and tangible book value
  - Net Asset Value (NAV) for asset-heavy industries
  - Liquidation value estimation
- **Earnings-Based Valuation**
  - Capitalized earnings method
  - Earnings power value (no-growth scenario)

### Advanced Features
- **🎯 Industry-Specific Weighting System**: Professional-grade approach that tailors valuation weights to each sector:
  - **Technology**: Emphasizes FCF models (60%) and EV/Sales (20%) for growth potential
  - **Consumer Staples**: Balanced approach with dividend focus and earnings stability
  - **Utilities**: Dividend-focused (30% DDM) with regulated asset base consideration
  - **Industrials**: FCFF emphasis (30%) and EV/EBITDA (25%) for capital-intensive operations
  - **Financials**: DDM-focused (40%) with book value emphasis (25%), excludes FCF models
  - **Energy**: Normalized cash flow approach (45%) with reserves-based NAV (20%)
  - **Healthcare**: Balanced growth and stability approach
- **Dynamic Adjustments**: Company-specific modifications for:
  - Non-dividend paying companies
  - High-growth characteristics (Beta > 1.5)
  - Large-cap mature companies (>$100B market cap)
  - High-leverage situations (D/E > 2)
- **Quality Controls**: Automatic exclusion/reduction of extreme valuations
- **Risk Assessment**: Comprehensive financial, business, and valuation risk analysis
- **Currency Support**: Automatic conversion for international companies
- **Confidence Scoring**: Statistical confidence measurement based on valuation consistency

## Installation

### Requirements
- Python 3.7+
- No external dependencies required (uses only Python standard library)

### Setup
```bash
# Clone or navigate to the python directory
cd python

# Optional: Install development dependencies
pip install -r requirements.txt

# The calculator is ready to use!
python src/calculate.py --help
```

## Usage

### Command Line Interface

```bash
# Calculate valuation for a specific company (default: CAT)
python src/calculate.py CAT

# List all available companies
python src/calculate.py --list

# Calculate and save results to JSON file
python src/calculate.py AAPL --save

# Show help
python src/calculate.py --help
```

### Programmatic Usage

```python
from src.valuation_calculator import ValuationCalculator
import json

# Load company data
with open('../data/cat.json', 'r') as f:
    company_data = json.load(f)

# Create calculator instance
calculator = ValuationCalculator(company_data)

# Calculate intrinsic value
results = calculator.calculate_intrinsic_value()

print(f"Intrinsic Value: ${results['intrinsicValue']:.2f}")
print(f"Current Price: ${results['currentPrice']:.2f}")
print(f"Upside: {results['upside']:.1f}%")
print(f"Recommendation: {results['recommendation']}")
```

## Project Structure

```
python/
├── src/
│   ├── valuation_calculator.py    # Main calculation engine
│   └── calculate.py               # Command-line interface
├── tests/
│   └── test_valuation_calculator.py  # Unit tests (to be created)
├── output/                        # Generated valuation reports
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Data Format

The calculator expects company data in JSON format with the following structure:

```json
{
  "ticker": "CAT",
  "companyName": "Caterpillar Inc.",
  "industry": "Farm & Heavy Construction Machinery",
  "sector": "Industrials",
  "marketData": {
    "currentPrice": 413.71,
    "marketCap": 194574000000,
    "sharesOutstanding": 470310000,
    "beta": 1.38
  },
  "financialHistory": {
    "TTM": {
      "revenue": 63259000000,
      "netIncome": 9939000000,
      "freeCashFlow": 7875000000,
      "totalAssets": 84974000000,
      "totalDebt": 38588000000,
      "shareholdersEquity": 18070000000,
      "eps": 20.51,
      "dividend": 6.04
    }
  },
  "keyRatios": {
    "valuationRatios": {
      "peRatio": 20.2,
      "pbRatio": 22.9,
      "evToEbitda": 15.8
    },
    "leverageRatios": {
      "debtToEquity": 2.14,
      "interestCoverage": 8.5
    }
  }
}
```

## Methodology

### Dynamic Weighting Algorithm

The calculator uses a sophisticated weighting system that adapts to company characteristics:

1. **Industry Analysis**: Cyclical companies receive higher weights for relative and asset-based methods
2. **Growth Stage**: Growth companies emphasize DCF methods over traditional metrics
3. **Financial Health**: High-debt companies favor FCFF over FCFE
4. **Market Position**: Large-cap mature companies emphasize earnings stability
5. **Quality Filters**: Extreme valuations are automatically down-weighted

### Risk Assessment Framework

- **Financial Risk**: Debt levels, liquidity ratios, interest coverage
- **Business Risk**: Beta, industry cyclicality, market volatility
- **Valuation Risk**: P/E ratio extremes, market multiples analysis

## Example Output

```
================================================================================
      INTRINSIC VALUE ANALYSIS: Caterpillar Inc. (CAT)
================================================================================

📊 EXECUTIVE SUMMARY
Current Price:     $413.71
Intrinsic Value:   $389.45
Potential Upside:  -5.9%
Margin of Safety:  6.2%
Recommendation:    Hold
Confidence Level:  High

🔍 DETAILED VALUATION BREAKDOWN

1. DISCOUNTED CASH FLOW MODELS:
   Free Cash Flow to Equity (FCFE):
   └─ Value per Share: $445.23
   └─ Upside: 7.6%
   └─ Discount Rate: 11.7%
   └─ Growth Rate: 8.0%

   Free Cash Flow to Firm (FCFF):
   └─ Value per Share: $398.17
   └─ Upside: -3.8%
   └─ WACC: 9.2%
   └─ Net Debt: $35.85B

📈 WEIGHTED VALUATION SUMMARY
   FCFE                                $445.23 (20% weight)
   FCFF                                $398.17 (20% weight)
   P/E Relative Valuation              $369.18 (20% weight)
   EV/EBITDA Relative Valuation        $412.50 (15% weight)
   Book Value                          $38.36  (5% weight)
   Capitalized Earnings                $425.67 (5% weight)
```

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Differences from JavaScript Version

The Python implementation maintains the same core logic and methodology as the JavaScript version but includes these improvements:

1. **Type Hints**: Full type annotations for better code documentation and IDE support
2. **Error Handling**: More robust error handling and validation
3. **Code Organization**: Better separation of concerns and modularity
4. **Documentation**: Comprehensive docstrings and comments
5. **Command Line Interface**: Enhanced CLI with argparse
6. **No External Dependencies**: Uses only Python standard library for core functionality

## Disclaimer

⚠️ **Important**: This tool is for educational and research purposes only. It does not constitute investment advice. Always consult with qualified financial professionals and conduct thorough research before making investment decisions.

## License

MIT License - see the main project LICENSE file for details.
