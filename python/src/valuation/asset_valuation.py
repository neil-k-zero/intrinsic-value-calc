#!/usr/bin/env python3
"""
Asset-based valuation methods.
"""

from __future__ import annotations
from typing import Dict, Any

from models.company_data import CompanyData
from models.valuation_result import ValuationResult


class AssetValuation:
    """
    Implements asset-based valuation methods.
    
    This class provides book value, tangible book value, and liquidation
    value calculations.
    """
    
    def __init__(self, company_data: CompanyData):
        """
        Initialize asset valuation calculator.
        
        Args:
            company_data: Normalized company data
        """
        self.company_data = company_data
    
    def calculate_book_value(self) -> ValuationResult:
        """
        Calculate book value per share.
        
        Returns:
            ValuationResult with book value calculation
        """
        try:
            current_price = self.company_data.get_current_price()
            shareholder_equity = self.company_data.get_latest_financial_data('shareholdersEquity')
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            if shareholder_equity <= 0:
                return ValuationResult.create_not_applicable(
                    'Book Value',
                    'Negative or zero shareholder equity'
                )
            
            book_value_per_share = shareholder_equity / shares_outstanding
            upside = ((book_value_per_share / current_price) - 1) * 100
            
            assumptions = {
                'shareholdersEquity': shareholder_equity,
                'sharesOutstanding': shares_outstanding,
                'priceToBook': current_price / book_value_per_share
            }
            
            return ValuationResult(
                method='Book Value',
                value_per_share=book_value_per_share,
                upside=upside,
                assumptions=assumptions
            )
            
        except Exception as e:
            return ValuationResult.create_not_applicable(
                'Book Value',
                f'Calculation error: {str(e)}'
            )
    
    def calculate_tangible_book_value(self) -> ValuationResult:
        """
        Calculate tangible book value per share.
        
        Returns:
            ValuationResult with tangible book value calculation
        """
        try:
            current_price = self.company_data.get_current_price()
            shareholder_equity = self.company_data.get_latest_financial_data('shareholdersEquity')
            goodwill = self.company_data.get_latest_financial_data('goodwill')
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            # Calculate tangible book value (remove intangible assets)
            tangible_book_value = shareholder_equity - goodwill
            
            if tangible_book_value <= 0:
                return ValuationResult.create_not_applicable(
                    'Tangible Book Value',
                    'Negative or zero tangible book value'
                )
            
            tangible_book_value_per_share = tangible_book_value / shares_outstanding
            upside = ((tangible_book_value_per_share / current_price) - 1) * 100
            
            assumptions = {
                'shareholdersEquity': shareholder_equity,
                'goodwill': goodwill,
                'tangibleBookValue': tangible_book_value,
                'sharesOutstanding': shares_outstanding
            }
            
            return ValuationResult(
                method='Tangible Book Value',
                value_per_share=tangible_book_value_per_share,
                upside=upside,
                assumptions=assumptions
            )
            
        except Exception as e:
            return ValuationResult.create_not_applicable(
                'Tangible Book Value',
                f'Calculation error: {str(e)}'
            )
    
    def calculate_liquidation_value(self) -> ValuationResult:
        """
        Calculate liquidation value per share.
        
        Returns:
            ValuationResult with liquidation value calculation
        """
        try:
            current_price = self.company_data.get_current_price()
            
            # Get asset values
            current_assets = self.company_data.get_latest_financial_data('currentAssets')
            total_assets = self.company_data.get_latest_financial_data('totalAssets')
            goodwill = self.company_data.get_latest_financial_data('goodwill')
            
            # Get liabilities
            total_liabilities = self.company_data.get_latest_financial_data('totalLiabilities')
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            # Apply liquidation discounts
            # Current assets: 85% recovery (cash, receivables, inventory)
            # Fixed assets: 60% recovery (property, equipment)
            # Intangible assets: 10% recovery (goodwill, patents)
            
            non_current_assets = total_assets - current_assets
            tangible_fixed_assets = non_current_assets - goodwill
            
            liquidation_value = (
                current_assets * 0.85 +          # Current assets at 85%
                tangible_fixed_assets * 0.60 +   # Fixed assets at 60%
                goodwill * 0.10 -                 # Intangibles at 10%
                total_liabilities                 # Full liabilities
            )
            
            if liquidation_value <= 0:
                return ValuationResult.create_not_applicable(
                    'Liquidation Value',
                    'Negative liquidation value'
                )
            
            liquidation_value_per_share = liquidation_value / shares_outstanding
            upside = ((liquidation_value_per_share / current_price) - 1) * 100
            
            assumptions = {
                'currentAssets': current_assets,
                'currentAssetsRecovery': 0.85,
                'fixedAssets': tangible_fixed_assets,
                'fixedAssetsRecovery': 0.60,
                'intangibleAssets': goodwill,
                'intangibleRecovery': 0.10,
                'totalLiabilities': total_liabilities,
                'liquidationValue': liquidation_value
            }
            
            return ValuationResult(
                method='Liquidation Value',
                value_per_share=liquidation_value_per_share,
                upside=upside,
                assumptions=assumptions
            )
            
        except Exception as e:
            return ValuationResult.create_not_applicable(
                'Liquidation Value',
                f'Calculation error: {str(e)}'
            )
