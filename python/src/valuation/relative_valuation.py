#!/usr/bin/env python3
"""
Relative valuation methods using market multiples.
"""

from __future__ import annotations
from typing import Dict, Any

from models.company_data import CompanyData
from models.valuation_result import ValuationResult
from utils.financial_calculations import FinancialCalculations


class RelativeValuation:
    """
    Implements relative valuation methods using market multiples.
    
    This class provides P/E ratio and EV/EBITDA valuation calculations
    based on sector-specific multiples.
    """
    
    def __init__(self, company_data: CompanyData):
        """
        Initialize relative valuation calculator.
        
        Args:
            company_data: Normalized company data
        """
        self.company_data = company_data
        self.calc = FinancialCalculations(company_data)
    
    def calculate_pe_valuation(self) -> ValuationResult:
        """
        Calculate P/E ratio based valuation.
        
        Returns:
            ValuationResult with P/E valuation
        """
        try:
            current_price = self.company_data.get_current_price()
            net_income = self.company_data.get_latest_financial_data('netIncome')
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            if net_income <= 0:
                return ValuationResult.create_not_applicable(
                    'P/E Valuation',
                    'Negative or zero net income'
                )
            
            # Calculate current P/E
            earnings_per_share = net_income / shares_outstanding
            current_pe = current_price / earnings_per_share
            
            # Get fair P/E multiple - prioritize company-specific benchmarks
            fair_pe = self._get_fair_pe_multiple()
            
            # Calculate fair value
            fair_value_per_share = earnings_per_share * fair_pe
            upside = ((fair_value_per_share / current_price) - 1) * 100
            
            assumptions = {
                'currentPE': current_pe,
                'fairPE': fair_pe,
                'earningsPerShare': earnings_per_share,
                'sector': self.company_data.sector
            }
            
            return ValuationResult(
                method='P/E Valuation',
                value_per_share=fair_value_per_share,
                upside=upside,
                assumptions=assumptions
            )
            
        except Exception as e:
            return ValuationResult.create_not_applicable(
                'P/E Valuation',
                f'Calculation error: {str(e)}'
            )
    
    def calculate_ev_ebitda_valuation(self) -> ValuationResult:
        """
        Calculate EV/EBITDA based valuation.
        
        Returns:
            ValuationResult with EV/EBITDA valuation
        """
        try:
            current_price = self.company_data.get_current_price()
            
            # Try to get explicit EBITDA first
            ebitda = self.company_data.get_latest_financial_data('ebitda')
            
            # If no explicit EBITDA, estimate it like the original calculator
            if ebitda <= 0:
                operating_income = self.company_data.get_latest_financial_data('operatingIncome')
                if operating_income > 0:
                    # Estimate EBITDA as Operating Income * 1.15 (same as original)
                    ebitda = operating_income * 1.15
                else:
                    return ValuationResult.create_not_applicable(
                        'EV/EBITDA Valuation',
                        'Cannot calculate EBITDA - no operating income data'
                    )
            
            if ebitda <= 0:
                return ValuationResult.create_not_applicable(
                    'EV/EBITDA Valuation',
                    'Negative or zero EBITDA'
                )
            
            # Calculate current metrics
            market_cap = self.company_data.get_market_cap()
            total_debt = self.company_data.get_latest_financial_data('totalDebt')
            cash = self.company_data.get_latest_financial_data('cash')
            
            enterprise_value = market_cap + total_debt - cash
            current_ev_ebitda = enterprise_value / ebitda
            
            # Get sector fair multiple
            fair_multiple = self._get_sector_ev_ebitda_multiple(self.company_data.sector)
            
            # Calculate fair enterprise value
            fair_ev = ebitda * fair_multiple
            
            # Calculate fair equity value
            fair_equity_value = fair_ev - total_debt + cash
            shares_outstanding = self.company_data.get_shares_outstanding()
            fair_value_per_share = fair_equity_value / shares_outstanding
            
            upside = ((fair_value_per_share / current_price) - 1) * 100
            
            assumptions = {
                'currentMultiple': current_ev_ebitda,
                'fairMultiple': fair_multiple,
                'ebitda': ebitda,
                'enterpriseValue': enterprise_value,
                'sector': self.company_data.sector
            }
            
            return ValuationResult(
                method='EV/EBITDA Valuation',
                value_per_share=fair_value_per_share,
                upside=upside,
                assumptions=assumptions
            )
            
        except Exception as e:
            return ValuationResult.create_not_applicable(
                'EV/EBITDA Valuation',
                f'Calculation error: {str(e)}'
            )
    
    def _get_fair_pe_multiple(self) -> float:
        """
        Get fair P/E multiple, prioritizing company-specific benchmarks over sector defaults.
        
        Returns:
            Fair P/E multiple
        """
        # First try to get company-specific benchmark from industryBenchmarks
        industry_benchmarks = self.company_data.raw_data.get('industryBenchmarks', {})
        if industry_benchmarks.get('averagePE'):
            return industry_benchmarks['averagePE']
        
        # Fall back to sector-based multiple
        return self._get_sector_pe_multiple(self.company_data.sector)
    
    def _get_sector_pe_multiple(self, sector: str) -> float:
        """
        Get sector-specific P/E multiple.
        
        Args:
            sector: Company sector
            
        Returns:
            Fair P/E multiple for the sector
        """
        sector_multiples = {
            'Technology': 22.0,
            'Healthcare': 18.0,
            'Consumer Discretionary': 20.0,
            'Communication Services': 16.0,
            'Industrials': 16.0,
            'Consumer Staples': 18.0,
            'Financials': 12.0,
            'Energy': 14.0,
            'Materials': 15.0,
            'Utilities': 16.0,
            'Real Estate': 20.0,
            'Biotechnology': 25.0
        }
        
        return sector_multiples.get(sector, 16.0)  # Default to 16x
    
    def _get_sector_ev_ebitda_multiple(self, sector: str) -> float:
        """
        Get sector-specific EV/EBITDA multiple.
        
        Args:
            sector: Company sector
            
        Returns:
            Fair EV/EBITDA multiple for the sector
        """
        sector_multiples = {
            'Technology': 15.0,
            'Healthcare': 14.0,
            'Consumer Discretionary': 12.0,
            'Communication Services': 10.0,
            'Industrials': 11.0,
            'Consumer Staples': 12.0,
            'Financials': 8.0,  # Banks often use P/E instead
            'Energy': 8.0,
            'Materials': 9.0,
            'Utilities': 10.0,
            'Real Estate': 16.0,
            'Biotechnology': 18.0
        }
        
        return sector_multiples.get(sector, 12.0)  # Default to 12x
