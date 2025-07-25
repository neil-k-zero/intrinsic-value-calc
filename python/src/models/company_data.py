#!/usr/bin/env python3
"""
CompanyData model for normalized company financial data.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class CompanyData:
    """
    Normalized company data structure for valuation calculations.
    
    This class provides structured access to company financial and market data
    with proper validation and type safety.
    """
    ticker: str
    company_name: str
    sector: str
    currency: str
    market_data: Dict[str, Any]
    financial_history: Dict[str, Dict[str, Any]]
    raw_data: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CompanyData:
        """
        Create CompanyData instance from dictionary.
        
        Args:
            data: Raw company data dictionary
            
        Returns:
            CompanyData instance
            
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ['ticker', 'companyName', 'marketData', 'financialHistory']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return cls(
            ticker=data['ticker'],
            company_name=data['companyName'],
            sector=data.get('sector', 'Unknown'),
            currency=data.get('currency', 'USD'),
            market_data=data['marketData'],
            financial_history=data['financialHistory'],
            raw_data=data
        )
    
    def get_current_price(self) -> float:
        """Get current stock price."""
        return self.market_data.get('currentPrice', 0)
    
    def get_shares_outstanding(self) -> float:
        """Get shares outstanding."""
        return self.market_data.get('sharesOutstanding', 0)
    
    def get_market_cap(self) -> float:
        """Calculate market capitalization."""
        return self.get_current_price() * self.get_shares_outstanding()
    
    def get_latest_financial_data(self, field: str) -> float:
        """
        Get most recent financial data for a specific field.
        
        Args:
            field: Financial data field name
            
        Returns:
            Latest value for the field
            
        Raises:
            ValueError: If no financial history available
        """
        if not self.financial_history:
            raise ValueError("No financial history available")
        
        # Get most recent year's data
        years = sorted(self.financial_history.keys(), reverse=True)
        latest_year = years[0]
        
        return self.financial_history[latest_year].get(field, 0)
    
    def get_financial_series(self, field: str, years: Optional[int] = None) -> Dict[str, float]:
        """
        Get time series of financial data for a specific field.
        
        Args:
            field: Financial data field name
            years: Number of years to retrieve (None for all)
            
        Returns:
            Dictionary mapping year to value
        """
        series = {}
        sorted_years = sorted(self.financial_history.keys(), reverse=True)
        
        if years:
            sorted_years = sorted_years[:years]
        
        for year in sorted_years:
            series[year] = self.financial_history[year].get(field, 0)
        
        return series
    
    def has_dividends(self) -> bool:
        """Check if company pays dividends."""
        try:
            # Check for dividend payment in latest financial data
            latest_dividend = self.get_latest_financial_data('dividend')
            if latest_dividend > 0:
                return True
            
            # Also check for dividendsPaid field
            dividends_paid = self.get_latest_financial_data('dividendsPaid')
            if dividends_paid > 0:
                return True
            
            # Check if dividendInfo section exists and has positive current dividend
            dividend_info = self.raw_data.get('dividendInfo', {})
            current_dividend = dividend_info.get('currentAnnualDividend', 0)
            if current_dividend > 0:
                return True
                
            return False
        except (ValueError, KeyError):
            return False
    
    def validate_required_data(self, required_fields: list[str]) -> None:
        """
        Validate that required financial data fields are present.
        
        Args:
            required_fields: List of required field names
            
        Raises:
            ValueError: If any required field is missing
        """
        if not self.financial_history:
            raise ValueError("No financial history available")
        
        latest_year = sorted(self.financial_history.keys(), reverse=True)[0]
        latest_data = self.financial_history[latest_year]
        
        for field in required_fields:
            if field not in latest_data:
                raise ValueError(f"Missing required financial field: {field}")
