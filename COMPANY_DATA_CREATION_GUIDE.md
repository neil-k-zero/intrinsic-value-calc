# Company Data File Creation Guide

## Overview

This guide provides a comprehensive process for creating company data files similar to `nvo.json` for use with the Company Value Calculator. The process combines data gathering from financial websites with computational tools to ensure complete and accurate valuation inputs.

## Data Sources

### Primary Source: StockAnalysis.com
**Best for**: US-listed companies and international companies with comprehensive coverage

**Key Pages to Collect Data From**:
1. **Overview Page** (`/stocks/[ticker]/`)
   - Current price, market cap, basic metrics
   - Company description and key facts

2. **Statistics Page** (`/stocks/[ticker]/statistics/`)
   - Comprehensive ratios and metrics
   - Share statistics and valuation multiples
   - Financial position metrics

3. **Financials Page** (`/stocks/[ticker]/financials/`)
   - Income statement data (5+ years)
   - Revenue, profits, margins

4. **Balance Sheet** (`/stocks/[ticker]/financials/balance-sheet/`)
   - Assets, liabilities, equity
   - Working capital components

5. **Cash Flow Statement** (`/stocks/[ticker]/financials/cash-flow-statement/`)
   - Operating, investing, financing cash flows
   - Free cash flow calculations

6. **Ratios Page** (`/stocks/[ticker]/financials/ratios/`)
   - Historical ratio trends
   - Efficiency and profitability metrics

### Supplementary Sources
- **Company IR Website**: Latest annual reports, investor presentations
- **SEC Filings**: 10-K, 10-Q for detailed financial data
- **Yahoo Finance**: Beta, analyst targets, dividend information
- **Bloomberg/Reuters**: Industry comparisons, analyst coverage

## Step-by-Step Process

### Phase 1: Initial Data Collection

#### 1.1 Basic Company Information
```json
{
  "ticker": "COMPANY_TICKER",
  "companyName": "Full Company Name",
  "industry": "Specific Industry Classification",
  "sector": "Broad Sector Category",
  "exchange": "NYSE/NASDAQ/etc",
  "lastUpdated": "YYYY-MM-DD"
}
```

#### 1.2 Market Data Collection
From overview and statistics pages:
- Current stock price
- Market capitalization
- Shares outstanding
- Enterprise value
- 52-week range
- Beta coefficient
- Analyst price targets

#### 1.3 Financial History Data
Collect 5-6 years of annual data:
- Revenue and growth rates
- Gross profit and margins
- Operating income
- Net income and EPS
- Free cash flow
- Total assets and debt
- Shareholders' equity
- Dividends per share

### Phase 2: Data Processing and Calculations

#### 2.1 Currency Normalization
For non-USD companies (like Novo Nordisk):

```bash
# Convert each financial metric from local currency to USD
python3 python/src/data_calculator.py convert \
  --amount [LOCAL_AMOUNT] \
  --from [LOCAL_CURRENCY] \
  --to USD \
  --rate [EXCHANGE_RATE]
```

**Example for DKK to USD**:
```bash
python3 python/src/data_calculator.py convert \
  --amount 290403000000 \
  --from DKK \
  --to USD \
  --rate 0.145
```

#### 2.2 Financial Ratio Calculations
Use the data calculator to compute missing ratios:

```bash
python3 python/src/data_calculator.py ratios \
  --revenue [REVENUE] \
  --gross-profit [GROSS_PROFIT] \
  --operating-income [OPERATING_INCOME] \
  --net-income [NET_INCOME] \
  --total-assets [TOTAL_ASSETS] \
  --total-debt [TOTAL_DEBT] \
  --shareholders-equity [SHAREHOLDERS_EQUITY] \
  --current-assets [CURRENT_ASSETS] \
  --current-liabilities [CURRENT_LIABILITIES]
```

#### 2.3 Growth Rate Analysis
Calculate historical growth metrics:

```bash
python3 python/src/data_calculator.py growth \
  --values "[YEAR1,YEAR2,YEAR3,YEAR4,YEAR5,YEAR6]"
```

**Example with NVO revenue data**:
```bash
python3 python/src/data_calculator.py growth \
  --values "18410000000,20420000000,25660000000,33680000000,42110000000,43920000000"
```

### Phase 3: Data File Construction

#### 3.1 Use Template Structure
Start with `data/template.json` and populate each section:

1. **Market Data Section**
2. **Financial History** (TTM + 5 historical years)
3. **Key Ratios** (calculated and verified)
4. **Growth Metrics**
5. **Dividend Information**
6. **Business Segments**
7. **Geographic Revenue**
8. **Risk Factors**

#### 3.2 Industry-Specific Adjustments

**Healthcare/Pharmaceuticals** (like NVO):
- Focus on R&D spending ratios
- Pipeline value considerations
- Regulatory risk factors
- Patent expiration schedules

**Technology Companies**:
- Revenue growth sustainability
- Customer acquisition costs
- Subscription metrics (if applicable)
- Innovation pipeline

**Financial Services**:
- Regulatory capital ratios
- Net interest margins
- Loan loss provisions
- Fee income stability

#### 3.3 Risk Factor Assessment
Customize risk factors based on:
- **Country Risk**: For international companies
- **Currency Risk**: For non-USD earnings
- **Industry Risk**: Sector-specific factors
- **Company-Specific Risk**: Competitive position, management, etc.

### Phase 4: Validation and Testing

#### 4.1 Data Validation
```bash
python3 python/src/data_calculator.py validate data/[company].json
```

**Target Score**: 90+ for reliable valuations

#### 4.2 Calculation Testing
```bash
python3 python/src/calculate.py [TICKER]
```

**Check for**:
- Reasonable valuation outputs
- No calculation errors
- Proper method weights
- Risk assessment accuracy

#### 4.3 Cross-Verification
Verify key metrics against multiple sources:
- Compare ratios with reported values
- Check growth calculations
- Validate market data consistency

## Common Challenges and Solutions

### Challenge 1: Missing Financial Data
**Solution**: Use estimation techniques
```bash
# Estimate EBITDA from operating income
estimated_ebitda = operating_income + (revenue * 0.05)

# Estimate free cash flow
estimated_fcf = operating_cash_flow - capex
```

### Challenge 2: Currency Conversion Consistency
**Solution**: Use consistent exchange rates throughout
- Document the exchange rate used
- Apply same rate to all financial periods
- Note currency conversion in data file

### Challenge 3: International Accounting Standards
**Solution**: Normalize to US GAAP equivalents where possible
- Research accounting differences
- Adjust for major discrepancies
- Document any assumptions made

### Challenge 4: Incomplete Dividend History
**Solution**: Use available data and mark incomplete sections
```json
"dividendInfo": {
  "note": "Limited dividend history available",
  "dataCompleteness": "3 years of data"
}
```

## Quality Control Checklist

### ✅ Data Completeness
- [ ] All required sections populated
- [ ] 5+ years of financial history
- [ ] Current market data (within 30 days)
- [ ] Industry benchmarks included

### ✅ Data Accuracy
- [ ] Currency conversion applied consistently
- [ ] Ratios match calculated values
- [ ] Growth rates reasonable and verified
- [ ] No obvious data entry errors

### ✅ Calculation Readiness
- [ ] All mandatory fields present
- [ ] Data types correct (numbers vs strings)
- [ ] Reasonable value ranges
- [ ] No circular references or conflicts

### ✅ Documentation Quality
- [ ] Clear currency notes
- [ ] Data source attribution
- [ ] Calculation assumptions documented
- [ ] Risk factors appropriate for company/industry

## Example: Novo Nordisk Creation Process

### Data Gathering (2 hours)
1. Collected from stockanalysis.com/stocks/nvo/
2. Gathered 6 years of financial data
3. Researched Danish healthcare industry factors
4. Identified GLP-1 market leadership position

### Data Processing (1 hour)
1. Converted DKK amounts to USD (rate: 0.145)
2. Calculated financial ratios using data_calculator.py
3. Verified growth rates and margins
4. Estimated missing EBITDA values

### File Construction (1.5 hours)
1. Populated template.json structure
2. Added healthcare-specific risk factors
3. Included detailed business segment data
4. Documented currency conversion assumptions

### Validation (30 minutes)
1. Achieved 100/100 data quality score
2. Successful valuation calculation
3. Reasonable $81.49 intrinsic value vs $71.02 current price
4. Proper method weighting for healthcare sector

## Templates for Different Industries

### Healthcare/Pharmaceuticals
```json
"riskFactors": {
  "riskFreeRate": 0.045,
  "equityRiskPremium": 0.055,
  "specificRiskPremium": 0.01,
  "regulatoryRisk": 0.005,
  "pipelineRisk": 0.010
}
```

### Technology
```json
"riskFactors": {
  "riskFreeRate": 0.045,
  "equityRiskPremium": 0.065,
  "specificRiskPremium": 0.015,
  "competitionRisk": 0.020,
  "innovationRisk": 0.010
}
```

### Utilities
```json
"riskFactors": {
  "riskFreeRate": 0.045,
  "equityRiskPremium": 0.045,
  "specificRiskPremium": 0.005,
  "regulatoryRisk": 0.010,
  "assetRisk": 0.005
}
```

## Automation Opportunities

### Future Enhancements
1. **API Integration**: Direct data feeds from financial APIs
2. **Automated Currency Conversion**: Real-time exchange rates
3. **Industry Template Selection**: Automatic risk factor adjustment
4. **Bulk Processing**: Handle multiple companies simultaneously
5. **Data Quality Monitoring**: Automatic validation and alerts

### Current Manual Steps
- Web scraping from financial sites
- Manual data entry and verification
- Currency conversion calculations
- Industry-specific customization
- Final quality assurance review

This comprehensive process ensures high-quality, accurate company data files that enable reliable intrinsic value calculations across different industries and markets.
