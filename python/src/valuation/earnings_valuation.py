#!/usr/bin/env python3
"""
Earnings-based valuation methods.
"""

from __future__ import annotations
from typing import Dict, Any

from models.company_data import CompanyData
from models.valuation_result import ValuationResult
from utils.financial_calculations import FinancialCalculations


class EarningsValuation:
    """
    Implements earnings-based valuation methods.
    
    This class provides capitalized earnings and earnings power
    value calculations.
    """
    
    def __init__(self, company_data: CompanyData):
        """
        Initialize earnings valuation calculator.
        
        Args:
            company_data: Normalized company data
        """
        self.company_data = company_data
        self.calc = FinancialCalculations(company_data)
    
    def calculate_capitalized_earnings(self) -> ValuationResult:
        """
        Calculate capitalized earnings valuation using average historical earnings.
        
        Returns:
            ValuationResult with capitalized earnings calculation
        """
        try:
            current_price = self.company_data.get_current_price()
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            # Get historical earnings data (same as original)
            earnings_history = self._get_earnings_history()
            if not earnings_history:
                return ValuationResult.create_not_applicable(
                    'Capitalized Earnings',
                    'No earnings history available'
                )
            
            # Calculate average earnings (same as original)
            avg_earnings = sum(earnings_history) / len(earnings_history)
            
            if avg_earnings <= 0:
                return ValuationResult.create_not_applicable(
                    'Capitalized Earnings',
                    'Negative or zero average earnings'
                )
            
            # Calculate cost of equity as capitalization rate
            capitalization_rate = self.calc.calculate_cost_of_equity()
            
            # Capitalize average earnings (same as original)
            capitalized_value = avg_earnings / capitalization_rate
            value_per_share = capitalized_value / shares_outstanding
            
            upside = ((value_per_share / current_price) - 1) * 100
            
            assumptions = {
                'avgEarnings': avg_earnings,
                'capitalizationRate': capitalization_rate,
                'totalValue': capitalized_value,
                'yearsOfHistory': len(earnings_history)
            }
            
            return ValuationResult(
                method='Capitalized Earnings',
                value_per_share=value_per_share,
                upside=upside,
                assumptions=assumptions
            )
            
        except Exception as e:
            return ValuationResult.create_not_applicable(
                'Capitalized Earnings',
                f'Calculation error: {str(e)}'
            )
    
    def calculate_earnings_power_value(self) -> ValuationResult:
        """
        Calculate earnings power value (normalized earnings capacity).
        
        Returns:
            ValuationResult with earnings power value calculation
        """
        try:
            current_price = self.company_data.get_current_price()
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            # Get historical earnings data
            earnings_history = self._get_earnings_history()
            if len(earnings_history) < 3:
                return ValuationResult.create_not_applicable(
                    'Earnings Power Value',
                    'Insufficient earnings history'
                )
            
            # Calculate normalized earnings (average of recent years)
            normalized_earnings = self._calculate_normalized_earnings(earnings_history)
            
            if normalized_earnings <= 0:
                return ValuationResult.create_not_applicable(
                    'Earnings Power Value',
                    'Negative or zero normalized earnings'
                )
            
            # Use cost of equity as discount rate (no growth assumption)
            discount_rate = self.calc.calculate_cost_of_equity()
            
            # Calculate earnings power value
            earnings_power_value = normalized_earnings / discount_rate
            value_per_share = earnings_power_value / shares_outstanding
            
            upside = ((value_per_share / current_price) - 1) * 100
            
            assumptions = {
                'normalizedEarnings': normalized_earnings,
                'earningsHistory': earnings_history,
                'discountRate': discount_rate,
                'earningsPowerValue': earnings_power_value,
                'normalizationMethod': 'Historical Average'
            }
            
            return ValuationResult(
                method='Earnings Power Value',
                value_per_share=value_per_share,
                upside=upside,
                assumptions=assumptions
            )
            
        except Exception as e:
            return ValuationResult.create_not_applicable(
                'Earnings Power Value',
                f'Calculation error: {str(e)}'
            )
    
    def _get_earnings_history(self) -> list[float]:
        """Get historical net income data."""
        earnings_data = self.company_data.get_financial_series('netIncome', 5)
        # Reverse the order to get chronological order (oldest first)
        earnings_values = [value for value in earnings_data.values() if value is not None]
        return list(reversed(earnings_values))
    
    def _calculate_normalized_earnings(self, earnings_history: list[float]) -> float:
        """
        Calculate normalized earnings using historical average.
        
        Args:
            earnings_history: List of historical earnings
            
        Returns:
            Normalized earnings amount
        """
        if not earnings_history:
            return 0.0
        
        # Remove extreme outliers (more than 2 standard deviations from mean)
        if len(earnings_history) >= 3:
            mean_earnings = sum(earnings_history) / len(earnings_history)
            
            # Calculate standard deviation
            variance = sum((e - mean_earnings) ** 2 for e in earnings_history) / len(earnings_history)
            std_dev = variance ** 0.5
            
            # Filter outliers if standard deviation is significant
            if std_dev > mean_earnings * 0.1:  # Only filter if volatility is > 10%
                filtered_earnings = [
                    e for e in earnings_history 
                    if abs(e - mean_earnings) <= 2 * std_dev
                ]
                if filtered_earnings:
                    earnings_history = filtered_earnings
        
        # Return average of remaining earnings
        return sum(earnings_history) / len(earnings_history)
