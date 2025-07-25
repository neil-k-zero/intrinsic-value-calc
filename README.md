# Company Value Calculator

A comprehensive intrinsic value calculator implemented in **Python** that uses multiple valuation methods to determine a company's fair value. This tool implements industry-standard approaches including DCF models, relative valuation, and asset-based methods.

## Features

### Valuation Methods Implemented

#### 1. Discounted Cash Flow (DCF) Models
- **Free Cash Flow to Equity (FCFE)**: Projects future free cash flows to equity holders
- **Free Cash Flow to Firm (FCFF)**: Values the entire firm then subtracts debt  
- **Dividend Discount Model (DDM)**: For dividend-paying stocks with Gordon Growth Model

#### 2. Relative Valuation Methods
- **P/E Ratio Analysis**: Compare to industry peers and historical averages
- **P/B Ratio Analysis**: Compare market value to book value
- **Enterprise Value Ratios**: EV/EBITDA, EV/Sales, EV/EBIT
- **PEG Ratio**: Growth-adjusted P/E analysis

#### 3. Asset-Based Approaches
- **Book Value**: Net worth from balance sheet
- **Liquidation Value**: Estimated liquidation proceeds
- **Replacement Value**: Cost to recreate assets

#### 4. Earnings-Based Methods
- **Capitalized Earnings**: Normalized earnings approach
- **Earnings Power Value**: Sustainable earnings without growth assumptions

## Quick Start

### Prerequisites
- Python 3.7 or higher
- No external dependencies required (uses Python standard library)

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/company-value-calculator.git
cd company-value-calculator

# Navigate to Python implementation
cd python

# Run a sample calculation
python src/calculate.py
```

## Usage

### Quick Start
```bash
cd python
python src/calculate.py --help
```

### Quick Start

```bash
# Calculate Caterpillar (CAT) valuation
python src/calculate.py CAT

# Calculate Apple (AAPL) and save to file 
python src/calculate.py AAPL --save

# List all available companies
python src/calculate.py --list
```

### Calculate Company Value
```bash
# Calculate using pre-loaded company data (default: CAT)
python src/calculate.py

# Calculate specific companies
python src/calculate.py CAT
python src/calculate.py AAPL --save

# List all available companies
python src/calculate.py --list
```

### Add New Company Data
1. Create a new JSON file in `data/` directory (e.g., `aapl.json`)
2. Follow the data structure format shown in `data/cat.json`
3. Run calculations: `python src/calculate.py AAPL`

## Data Structure

Each company data file should include:
- Stock information (ticker, price, shares outstanding)
- Financial statements (5+ years of income, balance sheet, cash flow)
- Market data (beta, risk-free rate, market risk premium)
- Growth assumptions and industry benchmarks

See `data/cat.json` for a complete example and `data/template.json` for the required structure.

## Example Output

The calculator provides:
- **Multiple valuation estimates** from different methods
- **Weighted average intrinsic value** using robust approach
- **Risk assessment** and confidence intervals
- **Detailed breakdown** of each valuation method
- **Recommendation** (Buy/Hold/Sell) with margin of safety

```
================================================================================
      INTRINSIC VALUE ANALYSIS: Caterpillar Inc. (CAT)
================================================================================

📊 EXECUTIVE SUMMARY
Current Price:     $413.71
Intrinsic Value:   $222.64
Potential Upside:  -46.2%
Margin of Safety:  6.2%
Recommendation:    Sell
Confidence Level:  High
```

## Project Structure

```
.
├── python/                          # Python implementation
│   ├── src/
│   │   ├── calculate.py             # Command-line interface  
│   │   ├── valuation_calculator_modular.py  # Main orchestrator
│   │   ├── data/                    # Data processing modules
│   │   ├── models/                  # Data models
│   │   ├── valuation/               # Valuation methods
│   │   ├── risk/                    # Risk analysis
│   │   ├── utils/                   # Utility functions
│   │   └── output/                  # Output formatting
│   ├── tests/
│   │   └── test_valuation_calculator.py  # Unit tests
│   └── README.md                    # Detailed Python documentation
├── data/                            # Company financial data
│   ├── nvo.json                     # Novo Nordisk example
│   ├── template.json                # Data structure template
│   └── [ticker].json                # Additional companies
└── README.md                        # This file
```

## Advanced Features

- **Industry-Specific Weighting**: Automatically adjusts valuation method weights based on company sector
- **Currency Support**: Handles international companies with automatic USD conversion
- **Risk Assessment**: Comprehensive financial, business, and valuation risk analysis
- **Professional Output**: Institutional-quality analysis reports
- **Comprehensive Testing**: Full test suite ensuring calculation accuracy

## How to ask AI agent for a company data file `ticker.json`

Create a new company data file similar to template.json but for NVIDIA Corporation (NVDA) nvda.json. Use the company data creation guide as a reference on how to calculate and generate this data. Reference the following links for company and stock financial data, metrics, and rations:

https://stockanalysis.com/stocks/nvda/
https://stockanalysis.com/stocks/nvda/statistics/
https://stockanalysis.com/stocks/nvda/financials/
https://stockanalysis.com/stocks/nvda/financials/balance-sheet/
https://stockanalysis.com/stocks/nvda/financials/cash-flow-statement/
https://stockanalysis.com/stocks/nvda/financials/ratios/
https://stockanalysis.com/stocks/nvda/revenue/
https://stockanalysis.com/stocks/nvda/metrics/
https://stockanalysis.com/stocks/nvda/market-cap/

## Investment Disclaimer

This tool is for educational and analytical purposes only. It does not constitute investment advice. Always consult with qualified financial professionals and conduct your own research before making investment decisions.

## License

MIT License - see LICENSE file for details
