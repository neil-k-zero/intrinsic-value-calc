# GitHub Copilot Instructions

## Project Overview

This is a **Python-based Company Value Calculator** that implements comprehensive intrinsic valuation methodologies for publicly traded companies. The project follows professional financial analysis standards and implements multiple valuation approaches including DCF models, relative valuation, and asset-based methods.

## Project Structure

```
.
├── python/                          # Main Python implementation
│   ├── src/
│   │   ├── valuation_calculator.py  # Core calculation engine (890+ lines)
│   │   └── calculate.py             # CLI interface (280+ lines)
│   ├── tests/
│   │   └── test_valuation_calculator.py  # Comprehensive unit tests
│   ├── output/                      # Generated valuation reports
│   ├── requirements.txt             # Python dependencies
│   └── README.md                    # Implementation guide
├── data/                            # Company financial data (JSON format)
│   ├── cat.json                     # Caterpillar example
│   ├── template.json                # Data structure template
│   └── [ticker].json                # Company-specific data files
└── output/                          # Legacy output directory
```

## Python Code Standards

### Language Standards
- **Python Version**: 3.8+ (use modern Python features like walrus operator, positional-only parameters)
- **Type Hints**: Use comprehensive type annotations throughout, including `from __future__ import annotations` for forward references
- **Docstrings**: Follow Google/NumPy docstring style with type information
- **Code Style**: Follow PEP 8 standards, use Black formatter
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Modern Features**: Utilize dataclasses, f-strings, pathlib, and context managers

### Key Dependencies
- **Core**: Python standard library only (no external dependencies for main functionality)
- **Optional**: pytest for testing, black for formatting, mypy for type checking
- **Data Format**: JSON for company financial data

### Code Organization Patterns

#### 1. Module Structure
```python
#!/usr/bin/env python3
"""
Module description.

Detailed module documentation explaining purpose and usage.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from decimal import Decimal
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants at module level
DEFAULT_RISK_FREE_RATE: float = 0.03
DEFAULT_MARKET_RISK_PREMIUM: float = 0.06
MINIMUM_FINANCIAL_HISTORY_YEARS: int = 3
```

#### 2. Class Design
```python
from dataclasses import dataclass
from typing import Protocol

@dataclass
class ValuationResult:
    """Dataclass for valuation method results."""
    method: str
    value_per_share: float
    upside: float
    assumptions: Dict[str, Any]
    not_applicable: bool = False
    reason: Optional[str] = None

class ValuationCalculator:
    """
    Comprehensive company valuation calculator.
    
    This class implements multiple valuation methodologies including DCF models,
    relative valuation, and asset-based approaches to determine intrinsic value.
    
    Attributes:
        data: Company financial and market data
        normalized_data: USD-converted financial data
        
    Example:
        >>> calculator = ValuationCalculator(company_data)
        >>> results = calculator.calculate_intrinsic_value()
    """
    
    def __init__(self, data: Dict[str, Any], /) -> None:
        """Initialize calculator with company data.
        
        Args:
            data: Company financial and market data dictionary
            
        Raises:
            ValueError: If required data fields are missing
        """
        self._validate_data(data)
        self.data = data
        self.normalized_data = self._normalize_currency(data)
        logger.info(f"Initialized calculator for {data.get('ticker', 'UNKNOWN')}")
    
    def _validate_data(self, data: Dict[str, Any]) -> None:
        """Validate required data fields with comprehensive checks."""
        required_sections = ['ticker', 'marketData', 'financialHistory']
        for section in required_sections:
            if section not in data:
                raise ValueError(f"Missing required section: {section}")
```

#### 3. Function Design
```python
def calculate_fcfe(self) -> Dict[str, Any]:
    """
    Calculate Free Cash Flow to Equity valuation.
    
    Implements multi-stage DCF model with declining growth rates
    and risk-adjusted discount rates.
    
    Returns:
        Dictionary containing:
            - valuePerShare: Calculated value per share
            - upside: Percentage upside vs current price
            - assumptions: Key calculation assumptions
            - notApplicable: Boolean if method not applicable
            - reason: Explanation if not applicable
            
    Raises:
        ValueError: If required financial data is missing
        TypeError: If data types are incorrect
    """
    pass
```

### Financial Calculation Standards

#### 1. Valuation Methods Implementation
```python
# DCF Models
def calculate_fcfe(self) -> Dict[str, Any]:  # Free Cash Flow to Equity
def calculate_fcff(self) -> Dict[str, Any]:  # Free Cash Flow to Firm  
def calculate_ddm(self) -> Dict[str, Any]:   # Dividend Discount Model

# Relative Valuation
def calculate_pe_valuation(self) -> Dict[str, Any]:      # P/E ratio analysis
def calculate_ev_ebitda_valuation(self) -> Dict[str, Any]: # EV/EBITDA multiples

# Asset-Based
def calculate_book_value(self) -> Dict[str, Any]:        # Book value approach
def calculate_liquidation_value(self) -> Dict[str, Any]: # Liquidation analysis

# Earnings-Based
def calculate_capitalized_earnings(self) -> Dict[str, Any]: # Earnings capitalization
```

#### 2. Financial Calculations
```python
def calculate_wacc(self) -> float:
    """Calculate Weighted Average Cost of Capital."""
    # Implementation: (E/V × Re) + (D/V × Rd × (1-T))
    
def calculate_cost_of_equity(self) -> float:
    """Calculate cost of equity using CAPM."""
    # Implementation: Rf + β(Rm - Rf) + Specific Risk Premium
    
def calculate_terminal_value(self, fcf: float, growth_rate: float, discount_rate: float) -> float:
    """Calculate terminal value using Gordon Growth Model."""
    # Implementation: FCF × (1 + g) / (r - g)
```

#### 3. Data Validation Patterns
```python
def _validate_financial_data(self) -> None:
    """Validate required financial data is present and valid."""
    required_fields = ['revenue', 'netIncome', 'freeCashFlow', 'totalDebt']
    
    for field in required_fields:
        if field not in self.data.get('financialHistory', {}).get('2024', {}):
            raise ValueError(f"Missing required field: {field}")
            
    # Validate data types and ranges
    current_price = self.data.get('marketData', {}).get('currentPrice')
    if not isinstance(current_price, (int, float)) or current_price <= 0:
        raise ValueError("Invalid current price")
```

### Error Handling Patterns

#### 1. Graceful Degradation
```python
def calculate_fcfe(self) -> Dict[str, Any]:
    """Calculate FCFE with graceful handling of edge cases."""
    try:
        # Main calculation logic
        value_per_share = self._calculate_fcfe_value()
        
        return {
            'method': 'FCFE',
            'valuePerShare': value_per_share,
            'upside': ((value_per_share / current_price) - 1) * 100,
            'assumptions': assumptions,
            'notApplicable': False
        }
        
    except (ValueError, ZeroDivisionError) as e:
        return {
            'method': 'FCFE',
            'valuePerShare': 0,
            'upside': 0,
            'notApplicable': True,
            'reason': f"Cannot calculate FCFE: {str(e)}"
        }
```

#### 2. Input Validation
```python
def load_company_data(ticker: str) -> Dict[str, Any]:
    """Load and validate company data from JSON file."""
    data_path = Path(f'data/{ticker.lower()}.json')
    
    if not data_path.exists():
        raise FileNotFoundError(f"Company data file not found: {data_path}")
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {data_path}: {e}")
    
    # Validate required structure
    required_sections = ['ticker', 'marketData', 'financialHistory']
    for section in required_sections:
        if section not in data:
            raise ValueError(f"Missing required section: {section}")
    
    return data
```

### Testing Standards

#### 1. Test Structure
```python
class TestValuationCalculator(unittest.TestCase):
    """Comprehensive test suite for ValuationCalculator."""
    
    def setUp(self) -> None:
        """Set up test data and calculator instance."""
        self.mock_data = {
            'ticker': 'TEST',
            'companyName': 'Test Company',
            # ... complete test data
        }
        self.calculator = ValuationCalculator(self.mock_data)
    
    def test_fcfe_calculation(self) -> None:
        """Test FCFE valuation calculation."""
        result = self.calculator.calculate_fcfe()
        
        self.assertEqual(result['method'], 'FCFE')
        self.assertIn('valuePerShare', result)
        self.assertGreater(result['valuePerShare'], 0)
        
    def test_fcfe_negative_cash_flow(self) -> None:
        """Test FCFE with negative cash flows."""
        # Test edge case handling
        pass
```

#### 2. Financial Data Testing
```python
def test_real_data_validation(self) -> None:
    """Test with real company data (CAT)."""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'cat.json'
    
    if data_path.exists():
        with open(data_path, 'r') as f:
            cat_data = json.load(f)
        
        calculator = ValuationCalculator(cat_data)
        results = calculator.calculate_intrinsic_value()
        
        # Validate results structure and reasonableness
        self.assertIn('intrinsicValue', results)
        self.assertGreater(results['intrinsicValue'], 0)
```

### CLI Development Standards

#### 1. Command Line Interface
```python
def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Calculate intrinsic value for publicly traded companies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/calculate.py CAT           # Analyze Caterpillar
  python src/calculate.py --list        # List available companies
  python src/calculate.py AAPL --save   # Analyze Apple and save results
        """
    )
    
    parser.add_argument('ticker', nargs='?', default='CAT',
                       help='Company ticker symbol (default: CAT)')
    parser.add_argument('--save', action='store_true',
                       help='Save results to JSON file')
    parser.add_argument('--list', action='store_true',
                       help='List all available companies')
    
    args = parser.parse_args()
```

#### 2. Output Formatting
```python
def print_valuation_results(results: Dict[str, Any], company_data: Dict[str, Any]) -> None:
    """Print comprehensive, professionally formatted results."""
    
    print('\n')
    print_divider(f"INTRINSIC VALUE ANALYSIS: {results['companyName']} ({results['ticker']})")
    
    print(f"\n📊 EXECUTIVE SUMMARY")
    print(f"Current Price:     {format_currency(results['currentPrice'])}")
    print(f"Intrinsic Value:   {format_currency(results['intrinsicValue'])}")
    print(f"Potential Upside:  {format_percent(results['upside'])}")
    print(f"Recommendation:    {results['recommendation']}")
```

## Domain-Specific Guidelines

### Financial Calculations
- **Precision**: Use Decimal for critical financial calculations where precision matters
- **Currency**: Handle multiple currencies with proper conversion rates
- **Growth Rates**: Implement declining growth models for realistic projections
- **Risk Adjustment**: Apply appropriate risk premiums based on company characteristics

### Data Handling
- **Validation**: Comprehensive validation of all financial inputs
- **Normalization**: Convert all financial data to consistent currency (USD)
- **Historical Data**: Require minimum 3-5 years of financial history
- **Missing Data**: Graceful handling with clear error messages

### Valuation Methodology
- **Multiple Methods**: Always implement multiple valuation approaches
- **Dynamic Weighting**: Adjust method weights based on company characteristics
- **Quality Controls**: Exclude extreme valuations from final calculation
- **Risk Assessment**: Comprehensive risk analysis framework

## Code Generation Guidelines

### When Adding New Features
1. **Financial Methods**: Follow existing calculation patterns with comprehensive error handling
2. **Data Processing**: Implement robust validation and currency conversion
3. **Output**: Maintain consistent formatting and professional presentation
4. **Testing**: Create comprehensive test cases including edge cases

### When Modifying Existing Code
1. **Backward Compatibility**: Maintain compatibility with existing data files
2. **Type Safety**: Preserve and enhance type annotations
3. **Documentation**: Update docstrings and comments
4. **Testing**: Ensure all existing tests continue to pass

### Code Quality Standards
- **Readability**: Write self-documenting code with clear variable names
- **Modularity**: Keep functions focused on single responsibilities
- **Performance**: Optimize for clarity over micro-optimizations
- **Maintainability**: Structure code for easy future modifications

## Common Patterns to Follow

### 1. Financial Data Access
```python
def get_latest_financial_data(self, field: str) -> float:
    """Get most recent financial data for a specific field."""
    history = self.normalized_data.get('financialHistory', {})
    
    # Get most recent year's data
    years = sorted(history.keys(), reverse=True)
    if not years:
        raise ValueError(f"No financial history available")
    
    latest_year = years[0]
    return history[latest_year].get(field, 0)
```

### 2. Currency Formatting
```python
def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format currency with appropriate symbols and precision."""
    if currency == 'DKK':
        return f"DKK {amount:,.2f}"
    else:
        return f"${amount:,.2f}"
```

### 3. Percentage Calculations
```python
def calculate_upside(intrinsic_value: float, current_price: float) -> float:
    """Calculate percentage upside/downside."""
    if current_price <= 0:
        raise ValueError("Current price must be positive")
    
    return ((intrinsic_value / current_price) - 1) * 100
```

## Important Notes

- **No JavaScript**: This is a pure Python project - avoid any JavaScript references
- **Financial Focus**: Prioritize financial accuracy and professional methodology
- **Educational Purpose**: Include appropriate investment disclaimers
- **Real Data**: Ensure compatibility with actual company financial data
- **Professional Output**: Generate institutional-quality analysis reports

## File Naming Conventions

- **Source Files**: `snake_case.py`
- **Test Files**: `test_*.py`
- **Data Files**: `{ticker}.json` (lowercase)
- **Output Files**: `{ticker}_valuation_{date}.json`
- **Documentation**: `UPPERCASE.md` for major docs, `lowercase.md` for others
