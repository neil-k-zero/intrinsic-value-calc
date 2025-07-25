#!/usr/bin/env python3
"""
Core financial calculations for valuation methods.
"""

from __future__ import annotations
import math
from typing import List

from models.company_data import CompanyData


class FinancialCalculations:
    """
    Core financial calculations used across valuation methods.
    
    This class provides fundamental financial calculations like WACC,
    cost of equity, growth rates, and other financial metrics.
    """
    
    # Default financial constants
    DEFAULT_RISK_FREE_RATE = 0.045  # 4.5% current US 10-year treasury
    DEFAULT_MARKET_RISK_PREMIUM = 0.06  # 6% historical market risk premium
    DEFAULT_TAX_RATE = 0.25  # 25% corporate tax rate
    
    def __init__(self, company_data: CompanyData):
        """
        Initialize financial calculations with company data.
        
        Args:
            company_data: Normalized company data
        """
        self.company_data = company_data
    
    def calculate_cost_of_equity(self) -> float:
        """
        Calculate cost of equity using CAPM model.
        
        Returns:
            Cost of equity as decimal (e.g., 0.12 for 12%)
        """
        # Get beta from market data
        beta = self.company_data.market_data.get('beta', 1.0)
        
        # Use risk factors from data if available, otherwise use defaults
        risk_factors = self.company_data.raw_data.get('riskFactors', {})
        risk_free_rate = risk_factors.get('riskFreeRate', self.DEFAULT_RISK_FREE_RATE)
        market_risk_premium = risk_factors.get('marketRiskPremium', self.DEFAULT_MARKET_RISK_PREMIUM)
        specific_risk_premium = risk_factors.get('specificRiskPremium', 0.0)
        
        cost_of_equity = risk_free_rate + (beta * market_risk_premium) + specific_risk_premium
        
        # Ensure reasonable bounds (4% to 25%)
        return max(0.04, min(0.25, cost_of_equity))
    
    def calculate_wacc(self) -> float:
        """
        Calculate Weighted Average Cost of Capital.
        
        Returns:
            WACC as decimal (e.g., 0.10 for 10%)
        """
        try:
            # Get financial data
            market_cap = self.company_data.get_market_cap()
            total_debt = self.company_data.get_latest_financial_data('totalDebt')
            
            # Calculate market values
            market_value_equity = market_cap
            market_value_debt = total_debt  # Assume book value approximates market value
            total_value = market_value_equity + market_value_debt
            
            # Calculate weights
            weight_equity = market_value_equity / total_value if total_value > 0 else 1.0
            weight_debt = market_value_debt / total_value if total_value > 0 else 0.0
            
            # Cost of equity
            cost_of_equity = self.calculate_cost_of_equity()
            
            # Cost of debt
            cost_of_debt = self._calculate_cost_of_debt()
            
            # Tax rate
            tax_rate = self._estimate_tax_rate()
            
            # WACC = (E/V × Re) + (D/V × Rd × (1-T))
            wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt * (1 - tax_rate))
            
            # Ensure reasonable bounds
            return max(0.04, min(0.20, wacc))
            
        except Exception:
            # Fallback to cost of equity if WACC calculation fails
            return self.calculate_cost_of_equity()
    
    def calculate_cagr(self, values: List[float]) -> float:
        """
        Calculate Compound Annual Growth Rate from a series of values.
        
        Args:
            values: List of values in chronological order
            
        Returns:
            CAGR as decimal (e.g., 0.05 for 5%)
        """
        if len(values) < 2:
            return 0.0
        
        # Remove any zero or negative values that would break the calculation
        positive_values = [v for v in values if v > 0]
        if len(positive_values) < 2:
            return 0.0
        
        beginning_value = positive_values[0]
        ending_value = positive_values[-1]
        periods = len(positive_values) - 1
        
        if beginning_value <= 0 or ending_value <= 0 or periods <= 0:
            return 0.0
        
        try:
            cagr = (ending_value / beginning_value) ** (1 / periods) - 1
            # Cap growth rates at reasonable levels
            return max(-0.50, min(0.50, cagr))
        except (ValueError, ZeroDivisionError, OverflowError):
            return 0.0
    
    def calculate_roe(self) -> float:
        """Calculate Return on Equity."""
        try:
            net_income = self.company_data.get_latest_financial_data('netIncome')
            shareholder_equity = self.company_data.get_latest_financial_data('shareholderEquity')
            
            if shareholder_equity <= 0:
                return 0.0
            
            return net_income / shareholder_equity
        except Exception:
            return 0.0
    
    def calculate_roa(self) -> float:
        """Calculate Return on Assets."""
        try:
            net_income = self.company_data.get_latest_financial_data('netIncome')
            total_assets = self.company_data.get_latest_financial_data('totalAssets')
            
            if total_assets <= 0:
                return 0.0
            
            return net_income / total_assets
        except Exception:
            return 0.0
    
    def calculate_debt_to_equity(self) -> float:
        """Calculate debt to equity ratio."""
        try:
            total_debt = self.company_data.get_latest_financial_data('totalDebt')
            shareholder_equity = self.company_data.get_latest_financial_data('shareholdersEquity')
            
            if shareholder_equity <= 0:
                return None  # Negative equity
            
            return total_debt / shareholder_equity
        except Exception:
            return None
    
    def calculate_current_ratio(self) -> float:
        """Calculate current ratio."""
        try:
            current_assets = self.company_data.get_latest_financial_data('currentAssets')
            current_liabilities = self.company_data.get_latest_financial_data('currentLiabilities')
            
            if current_liabilities <= 0:
                return None
            
            return current_assets / current_liabilities
        except Exception:
            return None
    
    def calculate_interest_coverage(self) -> float:
        """Calculate interest coverage ratio."""
        try:
            operating_income = self.company_data.get_latest_financial_data('operatingIncome')
            interest_expense = self.company_data.get_latest_financial_data('interestExpense')
            
            if interest_expense <= 0:
                return None  # No interest expense
            
            return operating_income / interest_expense
        except Exception:
            return None
    
    def _calculate_cost_of_debt(self) -> float:
        """Calculate cost of debt."""
        try:
            interest_expense = self.company_data.get_latest_financial_data('interestExpense')
            total_debt = self.company_data.get_latest_financial_data('totalDebt')
            
            if total_debt <= 0 or interest_expense <= 0:
                return self.DEFAULT_RISK_FREE_RATE + 0.02  # Risk-free rate + 2% spread
            
            cost_of_debt = interest_expense / total_debt
            
            # Ensure reasonable bounds
            return max(0.01, min(0.15, cost_of_debt))
            
        except Exception:
            return self.DEFAULT_RISK_FREE_RATE + 0.02
    
    def _estimate_tax_rate(self) -> float:
        """Estimate effective tax rate."""
        try:
            # Try to calculate from financial data
            net_income = self.company_data.get_latest_financial_data('netIncome')
            
            # Look for income before tax or use operating income
            income_before_tax = self.company_data.financial_history.get(
                max(self.company_data.financial_history.keys()), {}
            ).get('incomeBeforeTax')
            
            if not income_before_tax:
                operating_income = self.company_data.get_latest_financial_data('operatingIncome')
                interest_expense = self.company_data.get_latest_financial_data('interestExpense')
                income_before_tax = operating_income - interest_expense
            
            if income_before_tax > 0 and net_income is not None:
                tax_rate = 1 - (net_income / income_before_tax)
                return max(0.0, min(0.4, tax_rate))  # Cap between 0% and 40%
            
        except Exception:
            pass
        
        # Default to standard corporate tax rate
        return self.DEFAULT_TAX_RATE
    
    def _get_sector_risk_premium(self, sector: str) -> float:
        """
        Get sector-specific risk premium.
        
        Args:
            sector: Company sector
            
        Returns:
            Additional risk premium for the sector
        """
        sector_premiums = {
            'Technology': 0.01,
            'Biotechnology': 0.03,
            'Energy': 0.02,
            'Materials': 0.015,
            'Healthcare': 0.005,
            'Industrials': 0.01,
            'Communication Services': 0.01,
            'Consumer Discretionary': 0.01,
            'Consumer Staples': 0.005,
            'Utilities': 0.0,
            'Real Estate': 0.01,
            'Financials': 0.015
        }
        
        return sector_premiums.get(sector, 0.01)  # Default 1% premium
