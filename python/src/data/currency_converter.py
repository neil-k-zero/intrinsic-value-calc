#!/usr/bin/env python3
"""
Currency conversion utilities for financial data normalization.
"""

from __future__ import annotations
import copy
from typing import Dict, Any


class CurrencyConverter:
    """
    Handles currency conversion for financial data normalization.
    
    Currently supports DKK to USD conversion for companies with
    financial data in Danish Kroner.
    """
    
    @staticmethod
    def convert_to_usd(data: Dict[str, Any]) -> Dict[str, Any]:
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
            # Handle both simple number and dictionary exchange rate formats
            exchange_rate_data = data['exchangeRate']
            if isinstance(exchange_rate_data, dict):
                # Use dkkToUsd conversion rate from dictionary
                exchange_rate = exchange_rate_data.get('dkkToUsd', 0.1449)
            else:
                # Use direct number (DKK to USD rate)
                exchange_rate = exchange_rate_data
            
            # Convert all financial history data
            if 'financialHistory' in normalized_data:
                for year, year_data in normalized_data['financialHistory'].items():
                    CurrencyConverter._convert_financial_year_data(year_data, exchange_rate)
            
            # Convert dividend info to USD
            if normalized_data.get('dividendInfo'):
                dividend_info = normalized_data['dividendInfo']
                if dividend_info.get('currentAnnualDividend'):
                    dividend_info['currentAnnualDividend'] = dividend_info['currentAnnualDividend'] * exchange_rate
                if dividend_info.get('currentAnnualDividendUSD'):
                    # This is already in USD, don't convert
                    pass
            
            # Update currency marker
            normalized_data['currency'] = 'USD'
            normalized_data['originalCurrency'] = 'DKK'
            normalized_data['conversionRate'] = exchange_rate
        
        return normalized_data
    
    @staticmethod
    def _convert_financial_year_data(year_data: Dict[str, Any], exchange_rate: float) -> None:
        """
        Convert financial data for a single year to USD.
        
        Args:
            year_data: Dictionary containing financial data for one year
            exchange_rate: DKK to USD exchange rate
        """
        # Financial fields that need currency conversion (in millions)
        currency_fields = [
            'revenue', 'netIncome', 'totalAssets', 'totalLiabilities', 
            'shareholdersEquity', 'freeCashFlow', 'operatingCashFlow',
            'totalDebt', 'cash', 'dividendsPaid', 'capex', 'depreciation',
            'ebitda', 'operatingIncome', 'interestExpense', 'goodwill',
            'tangibleAssets', 'currentAssets', 'currentLiabilities',
            'longTermDebt', 'retainedEarnings', 'workingCapital',
            'cashAndEquivalents', 'totalEquity', 'grossProfit'
        ]
        
        for field in currency_fields:
            if field in year_data and year_data[field] is not None:
                # Convert from DKK millions to USD millions
                year_data[field] = year_data[field] * exchange_rate
        
        # Convert per-share values
        per_share_fields = ['bookValuePerShare', 'eps', 'dividend']
        for field in per_share_fields:
            if field in year_data and year_data[field] is not None:
                year_data[field] = year_data[field] * exchange_rate
    
    @staticmethod
    def get_display_currency(data: Dict[str, Any]) -> str:
        """
        Get the currency for displaying stock prices.
        
        Args:
            data: Company data dictionary
            
        Returns:
            Currency code for price display
        """
        market_data = data.get('marketData', {})
        return market_data.get('currentPriceCurrency', 'USD')
    
    @staticmethod
    def format_currency(amount: float, currency: str = 'USD') -> str:
        """
        Format currency amount for display.
        
        Args:
            amount: Amount to format
            currency: Currency code
            
        Returns:
            Formatted currency string
        """
        if currency == 'DKK':
            return f"DKK {amount:,.2f}"
        else:
            return f"${amount:,.2f}"
