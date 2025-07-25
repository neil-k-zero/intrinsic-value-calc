# Financial Data Calculator

A comprehensive Python utility for calculating financial metrics, validating company data files, and handling currency conversions for the Company Value Calculator project.

## Overview

The `data_calculator.py` script helps fill gaps in financial data that may not be readily available from stock analysis websites like stockanalysis.com. It provides essential calculations for creating comprehensive company valuation data files.

## Features

### 1. Financial Ratios Calculator
Calculate key financial ratios from basic financial statement data:

- **Profitability Ratios**: Gross margin, operating margin, net margin, ROA, ROE
- **Liquidity Ratios**: Current ratio, quick ratio, cash ratio
- **Leverage Ratios**: Debt-to-equity, debt-to-assets
- **Efficiency Ratios**: Asset turnover, inventory turnover, receivables turnover
- **Valuation Ratios**: P/E, P/B, Price-to-FCF, P/S ratios

### 2. Currency Conversion
Handle multi-currency financial data with built-in exchange rates:

- **Supported Currencies**: DKK, EUR, GBP, CAD, JPY, CHF to USD
- **Custom Rates**: Option to specify custom exchange rates
- **Bulk Conversion**: Process entire financial datasets

### 3. Growth Rate Analysis
Calculate various growth metrics from historical data:

- **Year-over-Year Growth**: Latest period growth rate
- **CAGR**: Compound Annual Growth Rate over multiple periods
- **Average Growth**: Mean annual growth rate

### 4. Data Validation
Comprehensive validation of company data files:

- **Required Fields Check**: Ensures all mandatory fields are present
- **Data Quality Scoring**: 0-100 quality score based on completeness
- **Missing Data Identification**: Lists missing or incomplete data points
- **Structure Validation**: Verifies proper JSON structure and data types

### 5. Missing Metrics Estimation
Estimate missing financial metrics using industry standards:

- **EBITDA Estimation**: Using operating income + estimated D&A
- **Free Cash Flow**: Operating cash flow - capital expenditures
- **Working Capital**: Current assets - current liabilities
- **Interest Coverage**: Operating income / interest expense

## Installation & Usage

### Prerequisites
```bash
cd /path/to/company-value-calculator
python3 -m pip install -r python/requirements.txt
```

### Command Line Interface

#### Calculate Financial Ratios
```bash
python3 python/src/data_calculator.py ratios \
  --revenue 43920000000 \
  --gross-profit 37180000000 \
  --operating-income 21270000000 \
  --net-income 15160000000 \
  --total-assets 70930000000 \
  --total-debt 17200000000 \
  --shareholders-equity 20070000000
```

#### Convert Currency
```bash
# Using predefined exchange rates
python3 python/src/data_calculator.py convert \
  --amount 1000 \
  --from DKK \
  --to USD

# Using custom exchange rate
python3 python/src/data_calculator.py convert \
  --amount 1000 \
  --from DKK \
  --to USD \
  --rate 0.145
```

#### Validate Data File
```bash
python3 python/src/data_calculator.py validate data/nvo.json
```

#### Calculate Growth Rates
```bash
python3 python/src/data_calculator.py growth \
  --values "18410000000,20420000000,25660000000,33680000000,42110000000,43920000000"
```

## Integration with Company Data Creation

### Step 1: Gather Base Data
Use stockanalysis.com and similar sources to collect:
- Market data (price, market cap, shares outstanding)
- Income statement data (revenue, profits, expenses)
- Balance sheet data (assets, liabilities, equity)
- Cash flow data (operating CF, capex, free cash flow)

### Step 2: Calculate Missing Ratios
```bash
# Example for Novo Nordisk
python3 python/src/data_calculator.py ratios \
  --revenue 43920000000 \
  --net-income 15160000000 \
  --total-assets 70930000000 \
  --shareholders-equity 20070000000
```

### Step 3: Convert Currency (if needed)
```bash
# Convert DKK financial data to USD
python3 python/src/data_calculator.py convert \
  --amount 290403000000 \
  --from DKK \
  --to USD \
  --rate 0.145
```

### Step 4: Calculate Growth Metrics
```bash
# Calculate revenue growth rates
python3 python/src/data_calculator.py growth \
  --values "18410000000,20420000000,25660000000,33680000000,42110000000,43920000000"
```

### Step 5: Validate Final Data File
```bash
python3 python/src/data_calculator.py validate data/your_company.json
```

## Example: Creating NVO Data File

The Novo Nordisk (NVO) data file was created using this process:

1. **Data Collection**: Gathered financial data from stockanalysis.com
2. **Currency Conversion**: Converted DKK amounts to USD using 0.145 exchange rate
3. **Ratio Calculation**: Used the calculator to verify financial ratios
4. **Growth Analysis**: Calculated 5-year revenue CAGR of 18.99%
5. **Validation**: Achieved 100/100 data quality score

### Key Calculations for NVO:
- **Revenue Growth (5Y CAGR)**: 18.99%
- **Gross Margin**: 84.65%
- **Operating Margin**: 48.43%
- **ROE**: 88.12%
- **Debt-to-Equity**: 0.86

## Built-in Exchange Rates (July 2025)

| Currency | Rate to USD |
|----------|-------------|
| DKK      | 0.145       |
| EUR      | 1.09        |
| GBP      | 1.27        |
| CAD      | 0.73        |
| JPY      | 0.0067      |
| CHF      | 1.12        |

## Error Handling

The calculator includes comprehensive error handling:

- **Division by Zero**: Handles cases where denominators are zero
- **Missing Data**: Gracefully skips calculations when required data is unavailable
- **Invalid Currency**: Provides clear error messages for unsupported currency pairs
- **File Validation**: Detailed reporting of data file issues

## Output Formats

### Financial Ratios Output
```
📊 CALCULATED FINANCIAL RATIOS
==================================================
Gross Margin: 0.8465
Operating Margin: 0.4843
Net Margin: 0.3452
Roa: 0.2137
Roe: 0.7554
Debt To Equity: 0.857
```

### Currency Conversion Output
```
💱 CURRENCY CONVERSION
==============================
Original Amount: 1,000.00 DKK
Converted Amount: 145.00 USD
Exchange Rate: 0.145
Note: Custom rate: 1 DKK = 0.145 USD
```

### Data Validation Output
```
🔍 DATA VALIDATION REPORT
========================================
File: data/nvo.json
Validation Passed: True
Data Quality Score: 100/100

✅ Data file is complete and well-structured!
```

### Growth Rate Analysis Output
```
📈 GROWTH RATE ANALYSIS
===================================
Yoy Growth: 4.30%
Cagr: 18.99%
Average Growth: 19.43%
```

## Integration with Main Calculator

The data calculator is designed to work seamlessly with the main valuation calculator:

1. **Data Preparation**: Use data_calculator.py to prepare comprehensive data files
2. **Validation**: Ensure data quality before running valuations
3. **Currency Consistency**: Convert all data to USD for consistent calculations
4. **Missing Data**: Estimate missing metrics to improve valuation accuracy

## Future Enhancements

Potential improvements to the data calculator:

1. **API Integration**: Direct integration with financial data APIs
2. **Industry Benchmarks**: Built-in industry ratio comparisons
3. **Batch Processing**: Process multiple companies simultaneously
4. **Advanced Estimates**: More sophisticated missing data estimation
5. **Export Features**: Direct export to JSON data file format

## Support

For issues or questions about the data calculator:

1. Check the main project documentation
2. Review the example usage in this README
3. Examine the NVO data file as a reference
4. Test calculations with known data to verify results

The data calculator is an essential tool for creating high-quality company data files that enable accurate intrinsic value calculations in the main valuation system.
