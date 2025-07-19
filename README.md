# Company Value Calculator

A comprehensive intrinsic value calculator that uses multiple valuation methods to determine a company's fair value. This tool implements industry-standard approaches including DCF models, relative valuation, and asset-based methods.

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

## Usage

### Quick Start
```bash
npm install
npm start
```

### Calculate Company Value
```bash
# Calculate using pre-loaded company data
npm run calculate

# Or run specific calculations
node src/calculate.js CAT
```

### Add New Company Data
1. Create a new JSON file in `data/` directory (e.g., `aapl.json`)
2. Follow the data structure format shown in `data/cat.json`
3. Run calculations: `node src/calculate.js AAPL`

## Data Structure

Each company data file should include:
- Stock information (ticker, price, shares outstanding)
- Financial statements (5+ years of income, balance sheet, cash flow)
- Market data (beta, risk-free rate, market risk premium)
- Growth assumptions and industry benchmarks

## Example Output

The calculator provides:
- **Multiple valuation estimates** from different methods
- **Weighted average intrinsic value** using robust approach
- **Risk assessment** and confidence intervals
- **Detailed breakdown** of each valuation method
- **Recommendation** (Buy/Hold/Sell) with margin of safety

## Investment Disclaimer

This tool is for educational and analytical purposes only. It does not constitute investment advice. Always consult with qualified financial professionals and conduct your own research before making investment decisions.

## License

MIT License - see LICENSE file for details
