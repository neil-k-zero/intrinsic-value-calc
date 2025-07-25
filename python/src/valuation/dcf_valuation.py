#!/usr/bin/env python3
"""
Discounted Cash Flow (DCF) valuation methods.

This module implements FCFE, FCFF, and DDM valuation approaches.
"""

from __future__ import annotations
import math
from typing import Dict, Any

from models.company_data import CompanyData
from models.valuation_result import ValuationResult
from utils.financial_calculations import FinancialCalculations
from utils.math_utils import MathUtils


class DCFValuation:
    """
    Implements Discounted Cash Flow valuation methods.
    
    This class provides FCFE (Free Cash Flow to Equity), FCFF (Free Cash Flow to Firm),
    and DDM (Dividend Discount Model) calculations.
    """
    
    def __init__(self, company_data: CompanyData):
        """
        Initialize DCF valuation calculator.
        
        Args:
            company_data: Normalized company data
        """
        self.company_data = company_data
        self.calc = FinancialCalculations(company_data)
    
    def calculate_fcfe(self) -> ValuationResult:
        """
        Calculate Free Cash Flow to Equity valuation.
        
        Returns:
            ValuationResult with FCFE calculation
        """
        try:
            # Get required data
            current_price = self.company_data.get_current_price()
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            # Get cash flow data
            fcf_history = self._get_fcf_history()
            if not fcf_history or all(fcf <= 0 for fcf in fcf_history):
                return ValuationResult.create_not_applicable(
                    'FCFE', 
                    'Negative or zero free cash flows',
                    self.calc.calculate_cost_of_equity()
                )
            
            # Calculate growth rate
            calculated_growth = self.calc.calculate_cagr(fcf_history)
            
            # Use conservative growth rate (same logic as original)
            predefined_growth = self.company_data.raw_data.get('growthMetrics', {}).get('fcfGrowth5Y', 0.10)
            initial_growth = min(calculated_growth, predefined_growth, 0.15)
            terminal_growth = 0.025  # 2.5% long-term growth
            
            # Calculate discount rate
            discount_rate = self.calc.calculate_cost_of_equity()
            
            # Project cash flows with declining growth (same as original)
            latest_fcf = fcf_history[-1]
            pv_sum = 0
            years_to_terminal = 5  # Use 5 years like original
            current_fcf = latest_fcf
            
            for year in range(1, years_to_terminal + 1):
                # Declining growth rate (same as original: growth * 0.85^(year-1))
                year_growth = initial_growth * (0.85 ** (year - 1))
                
                # Project cash flow
                current_fcf = current_fcf * (1 + year_growth)
                
                # Discount to present value
                pv = current_fcf / ((1 + discount_rate) ** year)
                pv_sum += pv
            
            # Calculate terminal value
            terminal_fcf = current_fcf * (1 + terminal_growth)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth)
            pv_terminal = terminal_value / ((1 + discount_rate) ** years_to_terminal)
            
            # Total value
            total_value = pv_sum + pv_terminal
            value_per_share = total_value / shares_outstanding
            upside = ((value_per_share / current_price) - 1) * 100
            
            assumptions = {
                'discountRate': discount_rate,
                'initialGrowth': initial_growth,
                'terminalGrowth': terminal_growth,
                'latestFCF': latest_fcf,
                'terminalValue': terminal_value
            }
            
            return ValuationResult(
                method='FCFE',
                value_per_share=value_per_share,
                upside=upside,
                assumptions=assumptions
            )
            
        except Exception as e:
            return ValuationResult.create_not_applicable(
                'FCFE', 
                f'Calculation error: {str(e)}',
                self.calc.calculate_cost_of_equity()
            )
    
    def calculate_fcff(self) -> ValuationResult:
        """
        Calculate Free Cash Flow to Firm valuation.
        
        Returns:
            ValuationResult with FCFF calculation
        """
        try:
            current_price = self.company_data.get_current_price()
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            # Get operating cash flow data
            ocf_history = self._get_operating_cash_flow_history()
            if not ocf_history or all(ocf <= 0 for ocf in ocf_history):
                return ValuationResult.create_not_applicable(
                    'FCFF', 
                    'Negative or zero operating cash flows'
                )
            
            # Calculate WACC
            wacc = self.calc.calculate_wacc()
            
            # Get latest financial data
            latest_ocf = self.company_data.get_latest_financial_data('operatingCashFlow')
            capex = self.company_data.get_latest_financial_data('capex')
            total_debt = self.company_data.get_latest_financial_data('totalDebt')
            
            # Calculate FCFF = Operating Cash Flow - CapEx + Tax Shield on Interest (same as original)
            interest_expense = total_debt * 0.04  # Estimated interest rate
            tax_rate = 0.25  # Default tax rate (same as original)
            tax_shield = interest_expense * tax_rate
            latest_fcff = latest_ocf - capex + tax_shield
            
            if latest_fcff <= 0:
                return ValuationResult.create_not_applicable(
                    'FCFF', 
                    'Negative Free Cash Flow to Firm'
                )
            
            # Growth projections (same as original)
            revenue_growth = self.company_data.raw_data.get('growthMetrics', {}).get('revenueGrowth5Y', 0.10)
            initial_growth = min(revenue_growth, 0.12)  # Cap at 12% like original
            terminal_growth = 0.025
            
            # Project FCFF for 10 years (same as original)
            firm_value = 0
            current_fcff = latest_fcff
            
            for year in range(1, 11):
                if year <= 5:
                    growth_rate = initial_growth
                else:
                    # Declining growth in years 6-10
                    growth_rate = initial_growth * (1 - (year - 5) / 5 * 0.7)
                
                current_fcff = current_fcff * (1 + growth_rate)
                pv = current_fcff / ((1 + wacc) ** year)
                firm_value += pv
            
            # Terminal value
            terminal_fcff = current_fcff * (1 + terminal_growth)
            terminal_value = terminal_fcff / (wacc - terminal_growth)
            pv_terminal = terminal_value / ((1 + wacc) ** 10)
            firm_value += pv_terminal
            
            # Subtract net debt to get equity value
            cash = self.company_data.get_latest_financial_data('cashAndEquivalents')
            net_debt = total_debt - cash
            equity_value = firm_value - net_debt
            value_per_share = equity_value / shares_outstanding
            upside = ((value_per_share / current_price) - 1) * 100
            
            assumptions = {
                'wacc': wacc,
                'initialGrowth': initial_growth,
                'terminalGrowth': terminal_growth,
                'netDebt': net_debt,
                'firmValue': firm_value
            }
            
            return ValuationResult(
                method='FCFF',
                value_per_share=value_per_share,
                upside=upside,
                assumptions=assumptions
            )
            
        except Exception as e:
            return ValuationResult.create_not_applicable(
                'FCFF', 
                f'Calculation error: {str(e)}'
            )
    
    def calculate_ddm(self) -> ValuationResult:
        """
        Calculate Dividend Discount Model valuation.
        
        Returns:
            ValuationResult with DDM calculation
        """
        try:
            current_price = self.company_data.get_current_price()
            
            # Get current dividend per share from latest financial data
            current_dividend = self.company_data.get_latest_financial_data('dividend')
            
            # Check if company pays dividends
            if current_dividend <= 0:
                return ValuationResult.create_not_applicable(
                    'DDM', 
                    'Company does not pay dividends'
                )
            
            # Get dividend growth rate from assumptions (like original calculator)
            assumptions_data = self.company_data.raw_data.get('assumptions', {})
            dividend_growth = assumptions_data.get('dividendGrowthRate', 0.06)  # Default 6%
            
            # Calculate required return
            required_return = self.calc.calculate_cost_of_equity()
            
            # Check if growth rate is reasonable
            if dividend_growth >= required_return:
                return ValuationResult.create_not_applicable(
                    'DDM', 
                    'Dividend growth rate exceeds required return'
                )
            
            # Gordon Growth Model
            next_dividend = current_dividend * (1 + dividend_growth)
            value_per_share = next_dividend / (required_return - dividend_growth)
            upside = ((value_per_share / current_price) - 1) * 100
            
            assumptions = {
                'currentDividend': current_dividend,
                'dividendGrowthRate': dividend_growth,
                'requiredReturn': required_return,
                'nextYearDividend': next_dividend
            }
            
            return ValuationResult(
                method='DDM',
                value_per_share=value_per_share,
                upside=upside,
                assumptions=assumptions
            )
            
        except Exception as e:
            return ValuationResult.create_not_applicable(
                'DDM', 
                f'Calculation error: {str(e)}'
            )
    
    def _get_fcf_history(self) -> list[float]:
        """Get historical free cash flow data."""
        fcf_data = self.company_data.get_financial_series('freeCashFlow', 5)
        # Reverse the order to get chronological order (oldest first) for CAGR calculation
        fcf_values = [value for value in fcf_data.values() if value is not None]
        return list(reversed(fcf_values))
    
    def _get_operating_cash_flow_history(self) -> list[float]:
        """Get historical operating cash flow data."""
        ocf_data = self.company_data.get_financial_series('operatingCashFlow', 5)
        # Reverse the order to get chronological order (oldest first) for CAGR calculation
        ocf_values = [value for value in ocf_data.values() if value is not None]
        return list(reversed(ocf_values))
    
    def _get_dividend_history(self) -> list[float]:
        """Get historical dividend payment data."""
        # Try dividendsPaid first (cash flow statement)
        dividend_data = self.company_data.get_financial_series('dividendsPaid', 5)
        dividend_values = [abs(value) for value in dividend_data.values() if value is not None and value != 0]
        
        # If no dividendsPaid data, try dividend field (income statement)
        if not dividend_values:
            dividend_data = self.company_data.get_financial_series('dividend', 5)
            dividend_values = [abs(value) for value in dividend_data.values() if value is not None and value != 0]
        
        # Reverse the order to get chronological order (oldest first) for CAGR calculation
        return list(reversed(dividend_values))
