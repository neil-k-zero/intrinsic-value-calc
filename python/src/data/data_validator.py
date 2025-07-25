#!/usr/bin/env python3
"""
Data validation utilities for company financial data.
"""

from __future__ import annotations
from typing import Dict, Any, List

from models.company_data import CompanyData


class DataValidator:
    """
    Validates company financial data for completeness and correctness.
    """
    
    # Required sections in company data
    REQUIRED_SECTIONS = ['ticker', 'companyName', 'marketData', 'financialHistory']
    
    # Required market data fields
    REQUIRED_MARKET_DATA = ['currentPrice', 'sharesOutstanding']
    
    # Required financial fields for calculations
    REQUIRED_FINANCIAL_FIELDS = [
        'revenue', 'netIncome', 'totalAssets',
        'shareholdersEquity', 'freeCashFlow'
    ]
    
    # Optional but important financial fields
    OPTIONAL_FINANCIAL_FIELDS = [
        'operatingCashFlow', 'totalDebt', 'cash', 'dividendsPaid',
        'capex', 'depreciation', 'ebitda', 'operatingIncome',
        'interestExpense', 'currentAssets', 'currentLiabilities', 'totalLiabilities'
    ]
    
    @classmethod
    def validate_raw_data(cls, data: Dict[str, Any]) -> None:
        """
        Validate raw company data structure.
        
        Args:
            data: Raw company data dictionary
            
        Raises:
            ValueError: If validation fails
        """
        # Check required sections
        for section in cls.REQUIRED_SECTIONS:
            if section not in data:
                raise ValueError(f"Missing required section: {section}")
        
        # Validate market data
        cls._validate_market_data(data.get('marketData', {}))
        
        # Validate financial history
        cls._validate_financial_history(data.get('financialHistory', {}))
    
    @classmethod
    def validate_company_data(cls, company_data: CompanyData) -> None:
        """
        Validate CompanyData object for valuation calculations.
        
        Args:
            company_data: CompanyData object to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Validate market data
        if company_data.get_current_price() <= 0:
            raise ValueError("Current price must be positive")
        
        if company_data.get_shares_outstanding() <= 0:
            raise ValueError("Shares outstanding must be positive")
        
        # Validate financial history
        if not company_data.financial_history:
            raise ValueError("No financial history available")
        
        # Check minimum years of data
        if len(company_data.financial_history) < 2:
            raise ValueError("Minimum 2 years of financial history required")
        
        # Validate latest year data
        try:
            company_data.validate_required_data(cls.REQUIRED_FINANCIAL_FIELDS)
        except ValueError as e:
            raise ValueError(f"Latest financial data incomplete: {e}")
    
    @classmethod
    def _validate_market_data(cls, market_data: Dict[str, Any]) -> None:
        """Validate market data section."""
        for field in cls.REQUIRED_MARKET_DATA:
            if field not in market_data:
                raise ValueError(f"Missing required market data field: {field}")
            
            value = market_data[field]
            if not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(f"Invalid value for {field}: {value}")
    
    @classmethod
    def _validate_financial_history(cls, financial_history: Dict[str, Any]) -> None:
        """Validate financial history section."""
        if not financial_history:
            raise ValueError("Financial history cannot be empty")
        
        # Check each year's data
        for year, year_data in financial_history.items():
            if not isinstance(year_data, dict):
                raise ValueError(f"Invalid financial data for year {year}")
            
            # Check for required fields in latest year
            if year == max(financial_history.keys()):
                missing_fields = []
                for field in cls.REQUIRED_FINANCIAL_FIELDS:
                    if field not in year_data or year_data[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    raise ValueError(f"Missing required fields in {year}: {missing_fields}")
    
    @classmethod
    def get_data_quality_report(cls, company_data: CompanyData) -> Dict[str, Any]:
        """
        Generate a data quality report for company data.
        
        Args:
            company_data: CompanyData object to assess
            
        Returns:
            Dictionary containing data quality metrics
        """
        report = {
            'overall_quality': 'Unknown',
            'years_available': len(company_data.financial_history),
            'missing_fields': [],
            'data_issues': [],
            'completeness_score': 0.0
        }
        
        # Check data completeness
        latest_year = max(company_data.financial_history.keys())
        latest_data = company_data.financial_history[latest_year]
        
        # Count available required fields
        available_required = sum(
            1 for field in cls.REQUIRED_FINANCIAL_FIELDS 
            if field in latest_data and latest_data[field] is not None
        )
        
        # Count available optional fields
        available_optional = sum(
            1 for field in cls.OPTIONAL_FINANCIAL_FIELDS 
            if field in latest_data and latest_data[field] is not None
        )
        
        # Calculate completeness score
        total_required = len(cls.REQUIRED_FINANCIAL_FIELDS)
        total_optional = len(cls.OPTIONAL_FINANCIAL_FIELDS)
        
        required_score = available_required / total_required
        optional_score = available_optional / total_optional
        
        # Weighted score (required fields are more important)
        report['completeness_score'] = (required_score * 0.8) + (optional_score * 0.2)
        
        # Determine overall quality
        if report['completeness_score'] >= 0.9:
            report['overall_quality'] = 'Excellent'
        elif report['completeness_score'] >= 0.8:
            report['overall_quality'] = 'Good'
        elif report['completeness_score'] >= 0.6:
            report['overall_quality'] = 'Fair'
        else:
            report['overall_quality'] = 'Poor'
        
        # Identify missing fields
        report['missing_fields'] = [
            field for field in cls.REQUIRED_FINANCIAL_FIELDS 
            if field not in latest_data or latest_data[field] is None
        ]
        
        # Check for data issues
        if report['years_available'] < 3:
            report['data_issues'].append('Limited historical data (< 3 years)')
        
        if company_data.get_latest_financial_data('shareholderEquity') <= 0:
            report['data_issues'].append('Negative or zero shareholder equity')
        
        if company_data.get_latest_financial_data('revenue') <= 0:
            report['data_issues'].append('Negative or zero revenue')
        
        return report
