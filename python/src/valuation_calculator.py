import json
import copy
import math
from datetime import datetime
from typing import Dict, List, Optional, Any


class ValuationCalculator:
    """
    A comprehensive company intrinsic value calculator using multiple valuation methods.
    
    This class implements various valuation approaches including:
    - Discounted Cash Flow (DCF) models (FCFE and FCFF)
    - Dividend Discount Model (DDM)
    - Relative valuation methods
    - Asset-based valuation
    - Earnings-based valuation
    """
    
    def __init__(self, company_data: Dict[str, Any]):
        """
        Initialize the valuation calculator with company data.
        
        Args:
            company_data: Dictionary containing all company financial and market data
        """
        self.data = company_data
        self.current_year = datetime.now().year
        
        # Handle currency conversion if needed
        self.normalized_data = self._convert_to_usd(company_data)
    
    def _convert_to_usd(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert financial data to USD if needed.
        
        Args:
            data: Company data dictionary
            
        Returns:
            Normalized data in USD
        """
        # If data is already in USD, return as-is
        if not data.get('currency') or data.get('currency') == 'USD':
            return data
        
        # Make a deep copy to avoid modifying original data
        normalized_data = copy.deepcopy(data)
        
        if data.get('currency') == 'DKK' and data.get('exchangeRate'):
            conversion_rate = data['exchangeRate']['dkkToUsd']
            
            # Convert financial history data from DKK to USD
            for year in normalized_data['financialHistory']:
                year_data = normalized_data['financialHistory'][year]
                
                # Convert monetary values (but not ratios, percentages, or share counts)
                monetary_fields = [
                    'revenue', 'grossProfit', 'operatingIncome', 'netIncome',
                    'freeCashFlow', 'operatingCashFlow', 'capex', 'totalAssets',
                    'totalDebt', 'cashAndEquivalents', 'shareholdersEquity',
                    'workingCapital', 'totalEquity', 'retainedEarnings'
                ]
                
                for field in monetary_fields:
                    if field in year_data and year_data[field] is not None:
                        year_data[field] = year_data[field] * conversion_rate
                
                # Convert per-share values
                if year_data.get('bookValuePerShare'):
                    year_data['bookValuePerShare'] = year_data['bookValuePerShare'] * conversion_rate
                if year_data.get('eps'):
                    year_data['eps'] = year_data['eps'] * conversion_rate
                if year_data.get('dividend'):
                    year_data['dividend'] = year_data['dividend'] * conversion_rate
            
            # Convert dividend info to USD
            if normalized_data.get('dividendInfo'):
                dividend_info = normalized_data['dividendInfo']
                if dividend_info.get('currentAnnualDividend'):
                    dividend_info['currentAnnualDividend'] = dividend_info['currentAnnualDividend'] * conversion_rate
            
            # Set currency to USD
            normalized_data['currency'] = 'USD'
        
        return normalized_data
    
    def calculate_fcfe(self) -> Dict[str, Any]:
        """
        Calculate Free Cash Flow to Equity (FCFE) valuation.
        
        Returns:
            Dictionary containing FCFE valuation results
        """
        years = sorted(self.normalized_data['financialHistory'].keys())
        latest_year = years[-1]
        latest_data = self.normalized_data['financialHistory'][latest_year]
        
        # Check if latest FCF is negative or zero - FCFE model not meaningful
        if latest_data['freeCashFlow'] <= 0:
            return {
                'method': 'FCFE',
                'valuePerShare': 0,
                'currentPrice': self.data['marketData']['currentPrice'],
                'upside': -100,
                'notApplicable': True,
                'reason': 'Negative free cash flow makes FCFE valuation unreliable',
                'assumptions': {
                    'initialGrowth': 0,
                    'terminalGrowth': self.data['assumptions']['terminalGrowthRate'],
                    'discountRate': self.calculate_cost_of_equity(),
                    'yearsProjected': 5
                }
            }
        
        # Calculate historical FCF growth
        fcf_history = [self.normalized_data['financialHistory'][year]['freeCashFlow'] for year in years]
        avg_growth_rate = self._calculate_cagr(fcf_history)
        
        # Use conservative growth rate
        initial_growth_rate = min(avg_growth_rate, self.data['growthMetrics']['fcfGrowth5Y'], 0.15)
        terminal_growth_rate = self.data['assumptions']['terminalGrowthRate']
        discount_rate = self.calculate_cost_of_equity()
        
        intrinsic_value = 0
        current_fcf = latest_data['freeCashFlow']
        
        # High growth period (years 1-5)
        for year in range(1, 6):
            growth_rate = initial_growth_rate * (0.85 ** (year - 1))  # Declining growth
            current_fcf = current_fcf * (1 + growth_rate)
            present_value = current_fcf / ((1 + discount_rate) ** year)
            intrinsic_value += present_value
        
        # Stable growth period (terminal value)
        terminal_fcf = current_fcf * (1 + terminal_growth_rate)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
        present_terminal_value = terminal_value / ((1 + discount_rate) ** 5)
        intrinsic_value += present_terminal_value
        
        value_per_share = intrinsic_value / self.data['marketData']['sharesOutstanding']
        
        return {
            'method': 'FCFE',
            'totalValue': intrinsic_value,
            'valuePerShare': value_per_share,
            'currentPrice': self.data['marketData']['currentPrice'],
            'upside': (value_per_share / self.data['marketData']['currentPrice'] - 1) * 100,
            'assumptions': {
                'initialGrowth': initial_growth_rate,
                'terminalGrowth': terminal_growth_rate,
                'discountRate': discount_rate,
                'yearsProjected': 5
            }
        }
    
    def calculate_fcff(self) -> Dict[str, Any]:
        """
        Calculate Free Cash Flow to Firm (FCFF) valuation.
        
        Returns:
            Dictionary containing FCFF valuation results
        """
        years = sorted(self.normalized_data['financialHistory'].keys())
        latest_year = years[-1]
        latest_data = self.normalized_data['financialHistory'][latest_year]
        
        # Calculate FCFF = Operating Cash Flow - CapEx + Tax Shield on Interest
        interest_expense = latest_data['totalDebt'] * 0.04  # Estimated interest rate
        tax_shield = interest_expense * self.data['assumptions']['taxRate']
        fcff = latest_data['operatingCashFlow'] - latest_data['capex'] + tax_shield
        
        wacc = self.calculate_wacc()
        terminal_growth_rate = self.data['assumptions']['terminalGrowthRate']
        initial_growth_rate = min(self.data['growthMetrics']['revenueGrowth5Y'], 0.12)
        
        firm_value = 0
        current_fcff = fcff
        
        # Project FCFF for 10 years
        for year in range(1, 11):
            if year <= 5:
                growth_rate = initial_growth_rate
            else:
                growth_rate = initial_growth_rate * (1 - (year - 5) / 5 * 0.7)
            
            current_fcff = current_fcff * (1 + growth_rate)
            present_value = current_fcff / ((1 + wacc) ** year)
            firm_value += present_value
        
        # Terminal value
        terminal_fcff = current_fcff * (1 + terminal_growth_rate)
        terminal_value = terminal_fcff / (wacc - terminal_growth_rate)
        present_terminal_value = terminal_value / ((1 + wacc) ** 10)
        firm_value += present_terminal_value
        
        # Subtract net debt to get equity value
        net_debt = latest_data['totalDebt'] - latest_data['cashAndEquivalents']
        equity_value = firm_value - net_debt
        value_per_share = equity_value / self.data['marketData']['sharesOutstanding']
        
        return {
            'method': 'FCFF',
            'firmValue': firm_value,
            'equityValue': equity_value,
            'valuePerShare': value_per_share,
            'currentPrice': self.data['marketData']['currentPrice'],
            'upside': (value_per_share / self.data['marketData']['currentPrice'] - 1) * 100,
            'assumptions': {
                'wacc': wacc,
                'initialGrowth': initial_growth_rate,
                'terminalGrowth': terminal_growth_rate,
                'netDebt': net_debt
            }
        }
    
    def calculate_ddm(self) -> Dict[str, Any]:
        """
        Calculate Dividend Discount Model (Gordon Growth Model) valuation.
        
        Returns:
            Dictionary containing DDM valuation results
        """
        years = sorted(self.normalized_data['financialHistory'].keys())
        latest_year = years[-1]
        latest_data = self.normalized_data['financialHistory'][latest_year]
        
        current_dividend = latest_data.get('dividend', 0)
        dividend_growth_rate = self.data['assumptions']['dividendGrowthRate']
        required_return = self.calculate_cost_of_equity()
        
        # Check if company pays dividends
        if current_dividend <= 0 or not current_dividend:
            return {
                'method': 'DDM (Gordon Growth)',
                'valuePerShare': 0,
                'currentPrice': self.data['marketData']['currentPrice'],
                'upside': -100,
                'notApplicable': True,
                'reason': 'Company does not pay dividends',
                'assumptions': {
                    'currentDividend': current_dividend,
                    'dividendGrowthRate': dividend_growth_rate,
                    'requiredReturn': required_return,
                    'nextYearDividend': 0
                }
            }
        
        # Check for reasonable dividend growth rate
        if dividend_growth_rate >= required_return:
            return {
                'method': 'DDM (Gordon Growth)',
                'valuePerShare': 0,
                'currentPrice': self.data['marketData']['currentPrice'],
                'upside': -100,
                'notApplicable': True,
                'reason': 'Dividend growth rate exceeds required return',
                'assumptions': {
                    'currentDividend': current_dividend,
                    'dividendGrowthRate': dividend_growth_rate,
                    'requiredReturn': required_return,
                    'nextYearDividend': 0
                }
            }
        
        # Gordon Growth Model: P = D1 / (r - g)
        next_year_dividend = current_dividend * (1 + dividend_growth_rate)
        value_per_share = next_year_dividend / (required_return - dividend_growth_rate)
        
        return {
            'method': 'DDM (Gordon Growth)',
            'valuePerShare': value_per_share,
            'currentPrice': self.data['marketData']['currentPrice'],
            'upside': (value_per_share / self.data['marketData']['currentPrice'] - 1) * 100,
            'assumptions': {
                'currentDividend': current_dividend,
                'dividendGrowthRate': dividend_growth_rate,
                'requiredReturn': required_return,
                'nextYearDividend': next_year_dividend
            }
        }
    
    def calculate_relative_valuation(self) -> Dict[str, Any]:
        """
        Calculate relative valuation using P/E, P/B, EV/EBITDA, and EV/Sales ratios.
        
        Returns:
            Dictionary containing relative valuation results
        """
        current_ratios = self.data['keyRatios']['valuationRatios']
        benchmarks = self.data['industryBenchmarks']
        years = sorted(self.normalized_data['financialHistory'].keys())
        latest_data = self.normalized_data['financialHistory'][years[-1]]
        sector = self.data.get('sector', '')
        
        results = {
            'peValuation': {
                'method': 'P/E Relative Valuation',
                'fairPE': benchmarks['averagePE'],
                'currentPE': current_ratios['peRatio'],
                'valuePerShare': latest_data['eps'] * benchmarks['averagePE'],
                'upside': ((latest_data['eps'] * benchmarks['averagePE']) / self.data['marketData']['currentPrice'] - 1) * 100
            },
            
            'pbValuation': {
                'method': 'P/B Relative Valuation',
                'fairPB': benchmarks['averagePB'],
                'currentPB': current_ratios['pbRatio'],
                'valuePerShare': latest_data['bookValuePerShare'] * benchmarks['averagePB'],
                'upside': ((latest_data['bookValuePerShare'] * benchmarks['averagePB']) / self.data['marketData']['currentPrice'] - 1) * 100
            },
            
            'evEbitdaValuation': {
                'method': 'EV/EBITDA Relative Valuation',
                'fairMultiple': self._get_sector_ev_ebitda_multiple(sector),
                'currentMultiple': current_ratios['evToEbitda'],
                'ebitda': latest_data['operatingIncome'] + (latest_data['operatingIncome'] * 0.15),  # Estimated EBITDA
                'enterpriseValue': self._calculate_fair_ev(latest_data['operatingIncome'] * 1.15, self._get_sector_ev_ebitda_multiple(sector)),
                'equityValue': self._calculate_fair_ev(latest_data['operatingIncome'] * 1.15, self._get_sector_ev_ebitda_multiple(sector)) - (latest_data['totalDebt'] - latest_data['cashAndEquivalents']),
                'valuePerShare': (self._calculate_fair_ev(latest_data['operatingIncome'] * 1.15, self._get_sector_ev_ebitda_multiple(sector)) - (latest_data['totalDebt'] - latest_data['cashAndEquivalents'])) / self.data['marketData']['sharesOutstanding']
            },
            
            'evSalesValuation': {
                'method': 'EV/Sales Relative Valuation',
                'fairMultiple': self._get_sector_ev_sales_multiple(sector),
                'currentMultiple': current_ratios.get('evToSales', 0),
                'revenue': latest_data['revenue'],
                'enterpriseValue': latest_data['revenue'] * self._get_sector_ev_sales_multiple(sector),
                'equityValue': (latest_data['revenue'] * self._get_sector_ev_sales_multiple(sector)) - (latest_data['totalDebt'] - latest_data['cashAndEquivalents']),
                'valuePerShare': ((latest_data['revenue'] * self._get_sector_ev_sales_multiple(sector)) - (latest_data['totalDebt'] - latest_data['cashAndEquivalents'])) / self.data['marketData']['sharesOutstanding']
            }
        }
        
        results['evEbitdaValuation']['upside'] = (results['evEbitdaValuation']['valuePerShare'] / self.data['marketData']['currentPrice'] - 1) * 100
        results['evSalesValuation']['upside'] = (results['evSalesValuation']['valuePerShare'] / self.data['marketData']['currentPrice'] - 1) * 100
        
        return results
    
    def _get_sector_ev_ebitda_multiple(self, sector: str) -> float:
        """
        Get sector-appropriate EV/EBITDA multiple.
        
        Args:
            sector: Company sector
            
        Returns:
            Sector-appropriate EV/EBITDA multiple
        """
        sector_multiples = {
            'Technology': 15.0,
            'Healthcare': 14.0,
            'Consumer Staples': 12.0,
            'Consumer Discretionary': 13.0,
            'Industrials': 11.0,
            'Financials': 0,  # Not applicable
            'Energy': 8.0,  # EBITDAX for oil & gas
            'Utilities': 10.0,
            'Communication Services': 12.0
        }
        return sector_multiples.get(sector, 12.0)  # Default to 12x
    
    def _get_sector_ev_sales_multiple(self, sector: str) -> float:
        """
        Get sector-appropriate EV/Sales multiple.
        
        Args:
            sector: Company sector
            
        Returns:
            Sector-appropriate EV/Sales multiple
        """
        sector_multiples = {
            'Technology': 5.0,  # Important for high-growth tech companies
            'Healthcare': 3.0,
            'Consumer Staples': 1.0,
            'Consumer Discretionary': 1.5,
            'Industrials': 1.0,
            'Financials': 0,  # Not applicable
            'Energy': 1.0,
            'Utilities': 2.0,
            'Communication Services': 3.0
        }
        return sector_multiples.get(sector, 2.0)  # Default to 2x
    
    def calculate_asset_based_valuation(self) -> Dict[str, Any]:
        """
        Calculate asset-based valuation including book value and liquidation value.
        
        Returns:
            Dictionary containing asset-based valuation results
        """
        years = sorted(self.normalized_data['financialHistory'].keys())
        latest_data = self.normalized_data['financialHistory'][years[-1]]
        
        return {
            'bookValue': {
                'method': 'Book Value',
                'valuePerShare': latest_data['bookValuePerShare'],
                'upside': (latest_data['bookValuePerShare'] / self.data['marketData']['currentPrice'] - 1) * 100
            },
            
            'tangibleBookValue': {
                'method': 'Tangible Book Value',
                'tangibleBV': latest_data['shareholdersEquity'] - (latest_data['totalAssets'] * 0.07),  # Estimated intangibles
                'valuePerShare': (latest_data['shareholdersEquity'] - (latest_data['totalAssets'] * 0.07)) / self.data['marketData']['sharesOutstanding'],
                'upside': ((latest_data['shareholdersEquity'] - (latest_data['totalAssets'] * 0.07)) / self.data['marketData']['sharesOutstanding'] / self.data['marketData']['currentPrice'] - 1) * 100
            },
            
            'liquidationValue': {
                'method': 'Liquidation Value (Conservative)',
                'recoveryRate': 0.7,
                'liquidationValue': latest_data['totalAssets'] * 0.7 - (latest_data['totalAssets'] - latest_data['shareholdersEquity']),
                'valuePerShare': (latest_data['totalAssets'] * 0.7 - (latest_data['totalAssets'] - latest_data['shareholdersEquity'])) / self.data['marketData']['sharesOutstanding'],
                'upside': ((latest_data['totalAssets'] * 0.7 - (latest_data['totalAssets'] - latest_data['shareholdersEquity'])) / self.data['marketData']['sharesOutstanding'] / self.data['marketData']['currentPrice'] - 1) * 100
            }
        }
    
    def calculate_earnings_based_valuation(self) -> Dict[str, Any]:
        """
        Calculate earnings-based valuation including capitalized earnings.
        
        Returns:
            Dictionary containing earnings-based valuation results
        """
        years = sorted(self.normalized_data['financialHistory'].keys())
        earnings_history = [self.normalized_data['financialHistory'][year]['netIncome'] for year in years]
        avg_earnings = sum(earnings_history) / len(earnings_history)
        
        cost_of_equity = self.calculate_cost_of_equity()
        capitalized_earnings = avg_earnings / cost_of_equity
        
        return {
            'capitalizedEarnings': {
                'method': 'Capitalized Earnings',
                'avgEarnings': avg_earnings,
                'capitalizationRate': cost_of_equity,
                'totalValue': capitalized_earnings,
                'valuePerShare': capitalized_earnings / self.data['marketData']['sharesOutstanding'],
                'upside': ((capitalized_earnings / self.data['marketData']['sharesOutstanding']) / self.data['marketData']['currentPrice'] - 1) * 100
            },
            
            'earningsPowerValue': {
                'method': 'Earnings Power Value (No Growth)',
                'normalizedEarnings': avg_earnings,
                'valuePerShare': (avg_earnings / self.data['marketData']['sharesOutstanding']) / cost_of_equity,
                'upside': (((avg_earnings / self.data['marketData']['sharesOutstanding']) / cost_of_equity) / self.data['marketData']['currentPrice'] - 1) * 100
            }
        }
    
    def calculate_cost_of_equity(self) -> float:
        """
        Calculate cost of equity using CAPM model.
        
        Returns:
            Cost of equity as a decimal
        """
        risk_free_rate = self.data['riskFactors']['riskFreeRate']
        beta = self.data['marketData']['beta']
        market_risk_premium = self.data['riskFactors']['marketRiskPremium']
        specific_risk = self.data['riskFactors']['specificRiskPremium']
        
        # CAPM: Re = Rf + β(Rm - Rf) + Specific Risk
        return risk_free_rate + beta * market_risk_premium + specific_risk
    
    def calculate_wacc(self) -> float:
        """
        Calculate Weighted Average Cost of Capital (WACC).
        
        Returns:
            WACC as a decimal
        """
        years = sorted(self.normalized_data['financialHistory'].keys())
        latest_data = self.normalized_data['financialHistory'][years[-1]]
        equity_value = self.data['marketData']['marketCap']
        debt_value = latest_data['totalDebt']
        total_value = equity_value + debt_value
        
        cost_of_equity = self.calculate_cost_of_equity()
        cost_of_debt = 0.04  # Estimated based on current rates
        tax_rate = self.data['assumptions']['taxRate']
        
        # WACC = (E/V * Re) + (D/V * Rd * (1-T))
        wacc = (equity_value / total_value) * cost_of_equity + \
               (debt_value / total_value) * cost_of_debt * (1 - tax_rate)
        
        return wacc
    
    def _calculate_cagr(self, values: List[float]) -> float:
        """
        Calculate Compound Annual Growth Rate (CAGR).
        
        Args:
            values: List of values to calculate CAGR for
            
        Returns:
            CAGR as a decimal
        """
        if len(values) < 2:
            return 0
        begin_value = values[0]
        end_value = values[-1]
        years = len(values) - 1
        return (end_value / begin_value) ** (1 / years) - 1
    
    def _calculate_fair_ev(self, ebitda: float, multiple: float) -> float:
        """
        Calculate fair enterprise value.
        
        Args:
            ebitda: EBITDA value
            multiple: EV/EBITDA multiple
            
        Returns:
            Fair enterprise value
        """
        return ebitda * multiple
    
    def calculate_industry_based_weights(self, fcfe_result: Dict, fcff_result: Dict, ddm_result: Dict,
                                        relative_results: Dict, asset_results: Dict, earnings_results: Dict) -> Dict[str, float]:
        """
        Calculate industry-specific weights for different valuation methods based on comprehensive industry analysis.
        
        Based on professional valuation best practices and industry characteristics.
        Weights are optimized for each sector's key value drivers and business characteristics.
        
        Args:
            fcfe_result: FCFE valuation results
            fcff_result: FCFF valuation results
            ddm_result: DDM valuation results
            relative_results: Relative valuation results
            asset_results: Asset-based valuation results
            earnings_results: Earnings-based valuation results
            
        Returns:
            Dictionary of weights for each valuation method
        """
        # Get sector and industry information
        sector = self.data.get('sector', '')
        industry = self.data.get('industry', '')
        
        # Industry-specific weight mappings based on comprehensive analysis
        # Reference: Professional valuation best practices by sector
        industry_weights = {
            # Technology (SaaS/Growth) - Focus: Future growth and cash flow potential
            'Technology': {
                'fcfe': 0.35,          # Intrinsic Models: 60%
                'fcff': 0.25,
                'ddm': 0.00,           # Rare dividends in growth tech
                'capitalizedEarnings': 0.00,  # Often unprofitable
                'peRelative': 0.05,    # Relative Models: 40%
                'evEbitda': 0.15,
                'evSales': 0.20,       # Key metric for unprofitable growth companies
                'bookValue': 0.00      # Asset-light businesses
            },
            
            # Consumer Staples - Focus: Stability and predictable returns
            'Consumer Staples': {
                'fcfe': 0.24,          # Intrinsic Models: 72%
                'fcff': 0.24,
                'ddm': 0.12,           # Consistent dividend payers
                'capitalizedEarnings': 0.12,  # Stable earnings
                'peRelative': 0.17,    # Relative Models: 28%
                'evEbitda': 0.11,
                'evSales': 0.00,       # Not typically used for mature staples
                'bookValue': 0.00      # Asset-Based Models: 0%
            },
            
            # Utilities - Focus: Dividends and regulated asset base
            'Utilities': {
                'fcfe': 0.20,          # Intrinsic Models: 60%
                'fcff': 0.15,
                'ddm': 0.30,           # Primary focus - income stocks
                'capitalizedEarnings': 0.10,  # Regulated earnings
                'peRelative': 0.15,    # Relative Models: 25%
                'evEbitda': 0.10,
                'evSales': 0.00,
                'bookValue': 0.10      # Regulated asset base matters
            },
            
            # Industrials/Manufacturing - Focus: Cyclical operations and capital intensity
            'Industrials': {
                'fcfe': 0.15,          # Intrinsic Models: 55%
                'fcff': 0.30,          # Better for capital-intensive businesses
                'ddm': 0.10,
                'capitalizedEarnings': 0.00,  # Earnings too cyclical
                'peRelative': 0.10,    # Relative Models: 35%
                'evEbitda': 0.25,      # Key metric - capital structure neutral
                'evSales': 0.00,
                'bookValue': 0.10      # Significant physical assets
            },
            
            # Banking/Financials - Focus: Regulatory capital, dividends, and book value
            'Financials': {
                'fcfe': 0.00,          # FCF models don't work - debt is raw material
                'fcff': 0.00,
                'ddm': 0.40,           # Primary measure of value to shareholders
                'capitalizedEarnings': 0.10,  # Standard earnings multiple
                'peRelative': 0.25,    # Industry standard comparison
                'evEbitda': 0.00,      # Not applicable to financials
                'evSales': 0.00,
                'bookValue': 0.25      # Regulatory capital and tangible book value
            },
            
            # Energy (Oil & Gas) - Focus: Commodity prices and proved reserves
            'Energy': {
                'fcfe': 0.15,          # Intrinsic Models: 50%
                'fcff': 0.30,          # Using normalized, mid-cycle prices
                'ddm': 0.05,           # Limited dividend focus due to volatility
                'capitalizedEarnings': 0.00,  # Earnings too unpredictable
                'peRelative': 0.00,    # P/E not reliable due to commodity volatility
                'evEbitda': 0.30,      # Industry-standard (EV/EBITDAX)
                'evSales': 0.00,
                'bookValue': 0.20      # NAV based on proved reserves
            },
            
            # Healthcare - Balanced approach between growth and stability
            'Healthcare': {
                'fcfe': 0.25,
                'fcff': 0.20,
                'ddm': 0.15,
                'capitalizedEarnings': 0.10,
                'peRelative': 0.20,
                'evEbitda': 0.10,
                'evSales': 0.00,
                'bookValue': 0.00
            },
            
            # Communication Services - Mix of mature and growth characteristics
            'Communication Services': {
                'fcfe': 0.30,
                'fcff': 0.20,
                'ddm': 0.10,
                'capitalizedEarnings': 0.05,
                'peRelative': 0.15,
                'evEbitda': 0.15,
                'evSales': 0.05,
                'bookValue': 0.00
            },
            
            # Consumer Discretionary - Similar to industrials but more cyclical
            'Consumer Discretionary': {
                'fcfe': 0.20,
                'fcff': 0.25,
                'ddm': 0.10,
                'capitalizedEarnings': 0.05,
                'peRelative': 0.15,
                'evEbitda': 0.20,
                'evSales': 0.05,
                'bookValue': 0.00
            }
        }
        
        # Real Estate (REITs) - Special case handling
        if 'REIT' in industry.upper() or 'Real Estate' in sector:
            industry_weights['Real Estate'] = {
                'fcfe': 0.00,          # Standard FCF models don't apply
                'fcff': 0.00,
                'ddm': 0.35,           # Mandatory high payouts (FFO-based)
                'capitalizedEarnings': 0.00,
                'peRelative': 0.35,    # P/FFO (Funds From Operations)
                'evEbitda': 0.00,
                'evSales': 0.00,
                'bookValue': 0.30      # NAV based on property portfolio value
            }
        
        # Get base weights for the sector
        if sector in industry_weights:
            weights = industry_weights[sector].copy()
        else:
            # Default to Consumer Staples weights (most balanced approach)
            weights = industry_weights['Consumer Staples'].copy()
        
        # Company-specific adjustments based on characteristics
        current_dividend = self.normalized_data['financialHistory'][sorted(self.normalized_data['financialHistory'].keys())[-1]].get('dividend', 0)
        dividend_yield = self.data.get('dividendInfo', {}).get('currentDividendYield', 0)
        beta = self.data['marketData']['beta']
        market_cap = self.data['marketData']['marketCap']
        debt_to_equity = self.data['keyRatios']['leverageRatios']['debtToEquity']
        
        # Handle non-dividend paying companies
        if current_dividend <= 0 or ddm_result.get('notApplicable'):
            ddm_weight = weights['ddm']
            weights['ddm'] = 0
            # Redistribute DDM weight based on sector characteristics
            if sector == 'Technology':
                weights['fcfe'] += ddm_weight * 0.4
                weights['evSales'] += ddm_weight * 0.4
                weights['evEbitda'] += ddm_weight * 0.2
            elif sector == 'Financials':
                weights['peRelative'] += ddm_weight * 0.6
                weights['bookValue'] += ddm_weight * 0.4
            else:
                weights['fcfe'] += ddm_weight * 0.4
                weights['fcff'] += ddm_weight * 0.3
                weights['peRelative'] += ddm_weight * 0.2
                weights['evEbitda'] += ddm_weight * 0.1
        
        # High-growth company adjustments (beta > 1.5)
        if beta > 1.5 and sector in ['Technology', 'Communication Services']:
            # Increase emphasis on forward-looking metrics
            weights['fcfe'] += 0.05
            weights['evSales'] = min(0.25, weights.get('evSales', 0) + 0.05)
            weights['peRelative'] = max(0.02, weights['peRelative'] - 0.05)
            weights['capitalizedEarnings'] = max(0.00, weights['capitalizedEarnings'] - 0.05)
        
        # Large cap mature companies (>$100B)
        if market_cap > 100000000000:
            if sector in ['Consumer Staples', 'Utilities', 'Healthcare']:
                weights['capitalizedEarnings'] += 0.05
                weights['ddm'] += 0.03 if current_dividend > 0 else 0
                weights['fcfe'] = max(0.10, weights['fcfe'] - 0.05)
                weights['fcff'] = max(0.10, weights['fcff'] - 0.03)
        
        # High debt adjustments
        if debt_to_equity and debt_to_equity > 2 and sector not in ['Financials']:
            # FCFF more appropriate than FCFE for highly leveraged companies
            fcfe_weight = weights['fcfe']
            weights['fcfe'] = max(0.05, weights['fcfe'] - 0.10)
            weights['fcff'] += fcfe_weight - weights['fcfe']
        
        # Quality checks - reduce weight for unreliable valuations
        current_price = self.data['marketData']['currentPrice']
        
        # Extreme valuation adjustments
        if fcfe_result.get('valuePerShare', 0) <= 0 or abs(fcfe_result.get('upside', 0)) > 150 or fcfe_result.get('notApplicable'):
            weights['fcfe'] = 0
        if fcff_result.get('valuePerShare', 0) <= 0 or abs(fcff_result.get('upside', 0)) > 150:
            weights['fcff'] = 0
        if ddm_result.get('valuePerShare', 0) <= 0 or abs(ddm_result.get('upside', 0)) > 150:
            weights['ddm'] = 0
        if relative_results.get('peValuation', {}).get('valuePerShare', 0) <= 0:
            weights['peRelative'] = 0
        if relative_results.get('evEbitdaValuation', {}).get('valuePerShare', 0) <= 0:
            weights['evEbitda'] = 0
        if relative_results.get('evSalesValuation', {}).get('valuePerShare', 0) <= 0:
            weights['evSales'] = 0
        if asset_results.get('bookValue', {}).get('valuePerShare', 0) <= 0:
            weights['bookValue'] = 0
        
        # Moderate extreme valuations by reducing their weights
        if abs(fcfe_result.get('upside', 0)) > 100:
            weights['fcfe'] *= 0.5
        if abs(fcff_result.get('upside', 0)) > 100:
            weights['fcff'] *= 0.5
        if abs(relative_results.get('peValuation', {}).get('upside', 0)) > 100:
            weights['peRelative'] *= 0.5
        if abs(relative_results.get('evEbitdaValuation', {}).get('upside', 0)) > 100:
            weights['evEbitda'] *= 0.5
        if abs(relative_results.get('evSalesValuation', {}).get('upside', 0)) > 100:
            weights['evSales'] *= 0.5
        
        # Ensure minimum representation for key methods where applicable
        if sector == 'Financials' and weights['bookValue'] == 0 and asset_results.get('bookValue', {}).get('valuePerShare', 0) > 0:
            weights['bookValue'] = 0.10
        if sector == 'Utilities' and weights['ddm'] == 0 and current_dividend > 0:
            weights['ddm'] = 0.15
        
        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        if total_weight > 0:
            for key in weights:
                weights[key] = weights[key] / total_weight
        else:
            # Fallback to equal weights if all methods failed
            num_methods = len(weights)
            for key in weights:
                weights[key] = 1.0 / num_methods
        
        return weights
    
    # Keep the old method name for backward compatibility
    def calculate_dynamic_weights(self, fcfe_result: Dict, fcff_result: Dict, ddm_result: Dict,
                                 relative_results: Dict, asset_results: Dict, earnings_results: Dict) -> Dict[str, float]:
        """
        Legacy method - redirects to new industry-based weights calculation.
        """
        return self.calculate_industry_based_weights(fcfe_result, fcff_result, ddm_result,
                                                   relative_results, asset_results, earnings_results)
    
    def calculate_confidence(self, valuations: List[Dict]) -> str:
        """
        Calculate confidence level based on valuation consistency.
        
        Args:
            valuations: List of valuation results
            
        Returns:
            Confidence level as string
        """
        values = [v['value'] for v in valuations]
        mean = sum(values) / len(values)
        variance = sum((val - mean) ** 2 for val in values) / len(values)
        std_dev = math.sqrt(variance)
        coefficient_of_variation = std_dev / mean
        
        # Lower CV = higher confidence
        if coefficient_of_variation < 0.2:
            return 'High'
        elif coefficient_of_variation < 0.4:
            return 'Medium'
        else:
            return 'Low'
    
    def calculate_risk_metrics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive risk metrics.
        
        Returns:
            Dictionary containing risk assessment
        """
        ratios = self.data['keyRatios']
        return {
            'financial': {
                'debtToEquity': ratios['leverageRatios']['debtToEquity'],
                'currentRatio': ratios['liquidityRatios']['currentRatio'],
                'interestCoverage': ratios['leverageRatios']['interestCoverage'],
                'riskLevel': self._assess_financial_risk(ratios)
            },
            'business': {
                'beta': self.data['marketData']['beta'],
                'volatilityRisk': 'High' if self.data['marketData']['beta'] > 1.5 else 'Medium' if self.data['marketData']['beta'] > 1 else 'Low',
                'industryRisk': 'Medium'  # Cyclical industry
            },
            'valuation': {
                'peRatio': ratios['valuationRatios']['peRatio'],
                'pbRatio': ratios['valuationRatios']['pbRatio'],
                'valuationRisk': 'High' if ratios['valuationRatios']['peRatio'] > 25 else 'Medium'
            }
        }
    
    def _assess_financial_risk(self, ratios: Dict) -> str:
        """
        Assess financial risk level.
        
        Args:
            ratios: Financial ratios dictionary
            
        Returns:
            Risk level as string
        """
        score = 0
        debt_to_equity = ratios['leverageRatios']['debtToEquity']
        current_ratio = ratios['liquidityRatios']['currentRatio']
        interest_coverage = ratios['leverageRatios']['interestCoverage']
        
        # Handle debt to equity (may be null for companies with negative equity)
        if debt_to_equity is not None:
            if debt_to_equity > 3:
                score += 2
            elif debt_to_equity > 2:
                score += 1
        else:
            # Negative equity is a significant risk factor
            score += 3
        
        if current_ratio and current_ratio < 1:
            score += 2
        elif current_ratio and current_ratio < 1.2:
            score += 1
        
        if interest_coverage and interest_coverage < 5:
            score += 2
        elif interest_coverage and interest_coverage < 10:
            score += 1
        
        if score >= 4:
            return 'High'
        elif score >= 2:
            return 'Medium'
        else:
            return 'Low'
    
    def get_recommendation(self, upside: float, margin_of_safety: float) -> str:
        """
        Get investment recommendation based on upside and margin of safety.
        
        Args:
            upside: Potential upside percentage
            margin_of_safety: Margin of safety percentage
            
        Returns:
            Investment recommendation
        """
        if upside > 20 and margin_of_safety > 15:
            return 'Strong Buy'
        elif upside > 10 and margin_of_safety > 10:
            return 'Buy'
        elif upside > 0 and margin_of_safety > 5:
            return 'Hold'
        elif upside > -10:
            return 'Hold'
        else:
            return 'Sell'
    
    def generate_summary(self, intrinsic_value: float, upside: float, 
                        margin_of_safety: float, recommendation: str) -> Dict[str, str]:
        """
        Generate investment summary.
        
        Args:
            intrinsic_value: Calculated intrinsic value
            upside: Potential upside percentage
            margin_of_safety: Margin of safety percentage
            recommendation: Investment recommendation
            
        Returns:
            Summary dictionary
        """
        return {
            'valuation': f"Based on comprehensive analysis using multiple valuation methods, {self.data['companyName']} has an estimated intrinsic value of ${intrinsic_value:.2f} per share.",
            'opportunity': f"The stock appears {'significantly ' if upside > 20 else ''}{'undervalued' if upside > 0 else 'overvalued'} with {abs(upside):.1f}% potential {'upside' if upside > 0 else 'downside'}.",
            'risk': f"Margin of safety: {margin_of_safety:.1f}%. {'Excellent' if margin_of_safety > 15 else 'Good' if margin_of_safety > 10 else 'Adequate' if margin_of_safety > 5 else 'Poor'} downside protection.",
            'recommendation': f"Investment recommendation: {recommendation}"
        }
    
    def get_weighting_rationale(self, weights: Dict[str, float]) -> List[str]:
        """
        Get explanation for weighting rationale based on industry-specific approach.
        
        Args:
            weights: Dictionary of weights
            
        Returns:
            List of rationale explanations
        """
        rationale = []
        sector = self.data.get('sector', '')
        industry = self.data.get('industry', '')
        current_dividend = self.normalized_data['financialHistory'][sorted(self.normalized_data['financialHistory'].keys())[-1]].get('dividend', 0)
        market_cap = self.data['marketData']['marketCap']
        beta = self.data['marketData']['beta']
        
        # Sector-specific rationale
        sector_explanations = {
            'Technology': "Technology company weights: Emphasizes future cash flow potential (60% intrinsic models) with EV/Sales for growth valuation. Minimal dividend and asset-based weights due to growth focus and asset-light business model.",
            'Consumer Staples': "Consumer Staples weights: Balanced approach emphasizing stability with strong FCF models (48%), consistent dividend focus (12%), and reliable earnings (12%). Reflects predictable business characteristics.",
            'Utilities': "Utilities weights: Dividend-focused approach (30% DDM) reflecting income-oriented nature. Includes regulated asset base consideration (10% book value) and stable cash flow emphasis.",
            'Industrials': "Industrials weights: Capital-intensive focus with strong FCFF emphasis (30%) and EV/EBITDA (25%) to handle cyclical earnings. Book value weight (10%) reflects significant physical assets.",
            'Financials': "Financials weights: Specialized approach with DDM focus (40%) and book value emphasis (25%) reflecting regulatory capital importance. FCF models excluded as debt is operational, not financing.",
            'Energy': "Energy weights: Commodity-focused with normalized cash flow emphasis (45% combined FCF) and reserves-based NAV (20%). EV/EBITDAX important for operational comparison (30%).",
            'Healthcare': "Healthcare weights: Balanced growth and stability approach with strong intrinsic model emphasis (70%) and moderate relative valuation weights reflecting R&D-intensive characteristics.",
            'Communication Services': "Communication Services weights: Mixed approach balancing mature telecom characteristics with growth potential in digital services.",
            'Consumer Discretionary': "Consumer Discretionary weights: Cyclical-adjusted approach with balanced DCF and relative methods, recognizing economic sensitivity."
        }
        
        if sector in sector_explanations:
            rationale.append(sector_explanations[sector])
        else:
            rationale.append("Default Consumer Staples weighting profile applied - balanced approach suitable for most stable businesses.")
        
        # Company-specific adjustments
        if current_dividend <= 0:
            rationale.append("Non-dividend paying company: DDM weight redistributed to cash flow and relative valuation methods")
        
        if beta > 1.5 and sector in ['Technology', 'Communication Services']:
            rationale.append("High-growth characteristics (Beta > 1.5): Enhanced focus on forward-looking valuation metrics")
        
        if market_cap > 100000000000:
            rationale.append("Large-cap mature company: Increased emphasis on earnings stability and dividend sustainability")
        
        debt_to_equity = self.data['keyRatios']['leverageRatios']['debtToEquity']
        if debt_to_equity and debt_to_equity > 2 and sector not in ['Financials']:
            rationale.append("High leverage (D/E > 2): FCFF emphasized over FCFE to better reflect enterprise value")
        
        # Quality adjustments
        extreme_valuations = []
        if weights.get('fcfe', 0) == 0:
            extreme_valuations.append("FCFE")
        if weights.get('fcff', 0) == 0:
            extreme_valuations.append("FCFF")
        if weights.get('ddm', 0) == 0 and current_dividend > 0:
            extreme_valuations.append("DDM")
        if weights.get('peRelative', 0) < 0.05:
            extreme_valuations.append("P/E")
        
        if extreme_valuations:
            rationale.append(f"Quality adjustment: {', '.join(extreme_valuations)} weight(s) reduced due to extreme valuation results")
        
        # Highlight key methodological strengths
        top_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
        method_names = {
            'fcfe': 'Free Cash Flow to Equity',
            'fcff': 'Free Cash Flow to Firm', 
            'ddm': 'Dividend Discount Model',
            'peRelative': 'P/E Relative Valuation',
            'evEbitda': 'EV/EBITDA Multiple',
            'evSales': 'EV/Sales Multiple',
            'bookValue': 'Book Value/NAV',
            'capitalizedEarnings': 'Capitalized Earnings'
        }
        
        top_methods = [f"{method_names.get(method, method)} ({weight:.1%})" for method, weight in top_weights if weight > 0.05]
        if top_methods:
            rationale.append(f"Primary valuation emphasis: {', '.join(top_methods)}")
        
        return rationale
    
    def calculate_intrinsic_value(self) -> Dict[str, Any]:
        """
        Calculate comprehensive intrinsic value using all valuation methods.
        
        Returns:
            Complete valuation analysis results
        """
        fcfe_result = self.calculate_fcfe()
        fcff_result = self.calculate_fcff()
        ddm_result = self.calculate_ddm()
        relative_results = self.calculate_relative_valuation()
        asset_results = self.calculate_asset_based_valuation()
        earnings_results = self.calculate_earnings_based_valuation()
        
        # Dynamic weight calculation based on company/industry characteristics
        weights = self.calculate_dynamic_weights(fcfe_result, fcff_result, ddm_result, 
                                               relative_results, asset_results, earnings_results)
        
        # Collect all value per share estimates with dynamic weights
        valuations = [
            {'method': fcfe_result['method'], 'value': fcfe_result['valuePerShare'], 'weight': weights['fcfe']},
            {'method': fcff_result['method'], 'value': fcff_result['valuePerShare'], 'weight': weights['fcff']},
            {'method': ddm_result['method'], 'value': ddm_result['valuePerShare'], 'weight': weights['ddm']},
            {'method': relative_results['peValuation']['method'], 'value': relative_results['peValuation']['valuePerShare'], 'weight': weights['peRelative']},
            {'method': relative_results['evEbitdaValuation']['method'], 'value': relative_results['evEbitdaValuation']['valuePerShare'], 'weight': weights['evEbitda']},
            {'method': relative_results['evSalesValuation']['method'], 'value': relative_results['evSalesValuation']['valuePerShare'], 'weight': weights.get('evSales', 0)},
            {'method': asset_results['bookValue']['method'], 'value': asset_results['bookValue']['valuePerShare'], 'weight': weights['bookValue']},
            {'method': earnings_results['capitalizedEarnings']['method'], 'value': earnings_results['capitalizedEarnings']['valuePerShare'], 'weight': weights['capitalizedEarnings']}
        ]
        
        # Calculate weighted average intrinsic value
        weighted_intrinsic_value = sum(val['value'] * val['weight'] for val in valuations)
        current_price = self.data['marketData']['currentPrice']
        upside = (weighted_intrinsic_value / current_price - 1) * 100
        
        # Risk assessment
        margin_of_safety = max(0, (weighted_intrinsic_value - current_price) / weighted_intrinsic_value * 100)
        recommendation = self.get_recommendation(upside, margin_of_safety)
        
        return {
            'ticker': self.data['ticker'],
            'companyName': self.data['companyName'],
            'currentPrice': current_price,
            'intrinsicValue': weighted_intrinsic_value,
            'upside': upside,
            'marginOfSafety': margin_of_safety,
            'recommendation': recommendation,
            'confidence': self.calculate_confidence(valuations),
            'valuationBreakdown': {
                'fcfe': fcfe_result,
                'fcff': fcff_result,
                'ddm': ddm_result,
                'relative': relative_results,
                'assetBased': asset_results,
                'earningsBased': earnings_results
            },
            'weightedValuations': valuations,
            'weightingRationale': self.get_weighting_rationale(weights),
            'riskMetrics': self.calculate_risk_metrics(),
            'summary': self.generate_summary(weighted_intrinsic_value, upside, margin_of_safety, recommendation)
        }
