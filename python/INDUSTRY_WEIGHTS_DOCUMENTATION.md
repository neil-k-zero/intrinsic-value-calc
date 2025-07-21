# Industry-Based Valuation Weights System

## Overview

The valuation calculator now uses a sophisticated industry-based weighting system that tailors valuation method weights to each sector's specific characteristics and value drivers. This approach follows professional valuation best practices and ensures that the most relevant valuation methods receive appropriate emphasis for each industry.

## Industry Weight Profiles

### Technology (SaaS/Growth Companies)
**Focus**: Future growth and cash flow potential

| Method | Weight | Rationale |
|--------|--------|-----------|
| FCFE | 35% | Primary intrinsic valuation for growth companies |
| FCFF | 25% | Supports FCFE for enterprise-wide analysis |
| DDM | 0% | Rare dividends in growth tech |
| Capitalized Earnings | 0% | Often unprofitable or low margins |
| P/E Relative | 5% | Limited relevance for growth/unprofitable companies |
| EV/EBITDA | 15% | Good operational comparison metric |
| EV/Sales | 20% | **Key metric for unprofitable growth companies** |
| Book Value/NAV | 0% | Asset-light business model |

**Key Features**:
- 60% weight on intrinsic models (FCFE + FCFF)
- 20% weight on EV/Sales for growth valuation
- Minimal emphasis on traditional earnings metrics

### Consumer Staples
**Focus**: Stability and predictable returns

| Method | Weight | Rationale |
|--------|--------|-----------|
| FCFE | 24% | Stable cash flow generation |
| FCFF | 24% | Consistent operational performance |
| DDM | 12% | Regular dividend payers |
| Capitalized Earnings | 12% | Predictable earnings streams |
| P/E Relative | 17% | Standard industry comparison |
| EV/EBITDA | 11% | Operational efficiency metric |
| EV/Sales | 0% | Not relevant for mature companies |
| Book Value/NAV | 0% | Asset values less critical |

**Key Features**:
- Balanced 72% intrinsic model weighting
- Strong emphasis on stability metrics
- Appropriate dividend consideration

### Utilities
**Focus**: Dividends and regulated asset base

| Method | Weight | Rationale |
|--------|--------|-----------|
| FCFE | 20% | Regulated cash flow streams |
| FCFF | 15% | Capital allocation focus |
| DDM | 30% | **Primary focus - income stocks** |
| Capitalized Earnings | 10% | Regulated earnings |
| P/E Relative | 15% | Industry comparison |
| EV/EBITDA | 10% | Operational efficiency |
| EV/Sales | 0% | Not applicable |
| Book Value/NAV | 10% | **Regulated asset base matters** |

**Key Features**:
- 30% DDM weight reflects income-oriented nature
- 10% book value weight for regulated asset base
- Lower overall FCF emphasis due to regulatory constraints

### Industrials/Manufacturing
**Focus**: Cyclical operations and capital intensity

| Method | Weight | Rationale |
|--------|--------|-----------|
| FCFE | 15% | Moderate cash flow focus |
| FCFF | 30% | **Better for capital-intensive businesses** |
| DDM | 10% | Some dividend consideration |
| Capitalized Earnings | 0% | **Earnings too cyclical** |
| P/E Relative | 10% | Limited reliability due to cycles |
| EV/EBITDA | 25% | **Key metric - capital structure neutral** |
| EV/Sales | 0% | Not typically used |
| Book Value/NAV | 10% | **Significant physical assets** |

**Key Features**:
- 30% FCFF weight for capital-intensive operations
- 25% EV/EBITDA weight for cyclical earnings
- No capitalized earnings due to cyclicality

### Banking/Financials
**Focus**: Regulatory capital, dividends, and book value

| Method | Weight | Rationale |
|--------|--------|-----------|
| FCFE | 0% | **FCF models don't work - debt is raw material** |
| FCFF | 0% | **Not applicable to financial business model** |
| DDM | 40% | **Primary measure of value to shareholders** |
| Capitalized Earnings | 10% | Standard earnings approach |
| P/E Relative | 25% | **Industry standard comparison** |
| EV/EBITDA | 0% | Not applicable to financials |
| EV/Sales | 0% | Not applicable to financials |
| Book Value/NAV | 25% | **Regulatory capital and tangible book value** |

**Key Features**:
- No FCF models - debt is operational, not financing
- 40% DDM emphasis for shareholder returns
- 25% book value weight for regulatory capital

### Energy (Oil & Gas)
**Focus**: Commodity prices and proved reserves

| Method | Weight | Rationale |
|--------|--------|-----------|
| FCFE | 15% | Moderate cash flow emphasis |
| FCFF | 30% | **Using normalized, mid-cycle prices** |
| DDM | 5% | Limited dividend focus due to volatility |
| Capitalized Earnings | 0% | **Earnings too unpredictable** |
| P/E Relative | 0% | **P/E not reliable due to commodity volatility** |
| EV/EBITDA | 30% | **Industry-standard (EV/EBITDAX)** |
| EV/Sales | 0% | Not typically used |
| Book Value/NAV | 20% | **NAV based on proved reserves** |

**Key Features**:
- 45% combined FCF weight with normalized assumptions
- 30% EV/EBITDAX for operational comparison
- 20% NAV for reserves-based valuation
- No P/E due to commodity price volatility

## Dynamic Adjustments

The system also applies company-specific adjustments:

### Non-Dividend Paying Companies
- DDM weight redistributed to other methods
- Technology companies: Additional weight to FCFE and EV/Sales
- Financials: Additional weight to P/E and Book Value
- Others: Redistributed to FCF and relative methods

### High-Growth Companies (Beta > 1.5)
- Enhanced focus on forward-looking metrics
- Increased FCFE and EV/Sales weights for tech companies
- Reduced emphasis on traditional earnings metrics

### Large-Cap Mature Companies (>$100B)
- Increased emphasis on earnings stability
- Enhanced DDM weight for dividend sustainability
- More conservative approach to growth assumptions

### High-Leverage Companies (D/E > 2)
- FCFF emphasized over FCFE
- Better reflection of enterprise value vs. equity value
- Does not apply to financials where debt is operational

### Quality Adjustments
- Extreme valuations (>150% upside/downside) are excluded
- Moderate extreme valuations (>100%) have weights reduced by 50%
- Negative or zero valuations are excluded
- Ensures reasonable final weighted result

## Implementation Benefits

1. **Professional Standards**: Based on industry best practices used by investment professionals
2. **Sector Relevance**: Each industry's key value drivers are properly weighted
3. **Adaptive System**: Automatically adjusts for company-specific characteristics
4. **Quality Controls**: Prevents extreme valuations from distorting results
5. **Transparency**: Clear rationale provided for weighting decisions

## Usage in Reports

The system now provides detailed explanations in valuation reports:
- Sector-specific rationale for base weights
- Company-specific adjustments made
- Quality control measures applied
- Primary valuation methods emphasized

This ensures users understand why certain methods are emphasized and builds confidence in the valuation approach.
