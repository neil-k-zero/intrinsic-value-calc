#!/usr/bin/env python3
"""
Main ValuationCalculator class that orchestrates all valuation methods.

This modular implementation replaces the original monolithic calculator
with focused, single-responsibility components.
"""

from __future__ import annotations
from typing import Dict, Any, List

from models.company_data import CompanyData
from models.valuation_result import ValuationResult
from models.risk_metrics import RiskMetrics
from data.data_validator import DataValidator
from valuation.dcf_valuation import DCFValuation
from valuation.relative_valuation import RelativeValuation
from valuation.asset_valuation import AssetValuation
from valuation.earnings_valuation import EarningsValuation
from risk.risk_analyzer import RiskAnalyzer
from output.result_formatter import ResultFormatter


class ValuationCalculator:
    """
    Main valuation calculator orchestrating all valuation methods.
    
    This class coordinates the various valuation approaches to produce
    a comprehensive intrinsic value analysis.
    """
    
    def __init__(self, company_data: CompanyData):
        """
        Initialize the valuation calculator.
        
        Args:
            company_data: Normalized company data object
        """
        # Validate data
        DataValidator.validate_company_data(company_data)
        
        self.company_data = company_data
        
        # Initialize valuation modules
        self.dcf_valuation = DCFValuation(company_data)
        self.relative_valuation = RelativeValuation(company_data)
        self.asset_valuation = AssetValuation(company_data)
        self.earnings_valuation = EarningsValuation(company_data)
        self.risk_analyzer = RiskAnalyzer(company_data)
    
    def calculate_intrinsic_value(self) -> Dict[str, Any]:
        """
        Calculate comprehensive intrinsic value using all methods.
        
        Returns:
            Complete valuation results dictionary
        """
        # Calculate all valuation methods
        dcf_results = self._calculate_dcf_methods()
        relative_results = self._calculate_relative_methods()
        asset_results = self._calculate_asset_methods()
        earnings_results = self._calculate_earnings_methods()
        
        # Analyze risks
        risk_metrics = self.risk_analyzer.analyze_all_risks()
        
        # Calculate weighted valuation
        weighted_valuations = self._calculate_weighted_valuation(
            dcf_results, relative_results, asset_results, earnings_results
        )
        
        # Calculate final intrinsic value
        final_intrinsic_value = self._calculate_final_value(weighted_valuations)
        
        # Format comprehensive results
        return ResultFormatter.create_comprehensive_result(
            company_data=self.company_data,
            dcf_results=dcf_results,
            relative_results=relative_results,
            asset_results=asset_results,
            earnings_results=earnings_results,
            risk_metrics=risk_metrics,
            weighted_valuations=weighted_valuations,
            final_intrinsic_value=final_intrinsic_value
        )
    
    def _calculate_dcf_methods(self) -> Dict[str, ValuationResult]:
        """Calculate all DCF-based valuation methods."""
        return {
            'fcfe': self.dcf_valuation.calculate_fcfe(),
            'fcff': self.dcf_valuation.calculate_fcff(),
            'ddm': self.dcf_valuation.calculate_ddm()
        }
    
    def _calculate_relative_methods(self) -> Dict[str, ValuationResult]:
        """Calculate all relative valuation methods."""
        return {
            'pe': self.relative_valuation.calculate_pe_valuation(),
            'ev_ebitda': self.relative_valuation.calculate_ev_ebitda_valuation()
        }
    
    def _calculate_asset_methods(self) -> Dict[str, ValuationResult]:
        """Calculate all asset-based valuation methods."""
        return {
            'book_value': self.asset_valuation.calculate_book_value(),
            'tangible_book_value': self.asset_valuation.calculate_tangible_book_value(),
            'liquidation_value': self.asset_valuation.calculate_liquidation_value()
        }
    
    def _calculate_earnings_methods(self) -> Dict[str, ValuationResult]:
        """Calculate all earnings-based valuation methods."""
        return {
            'capitalized_earnings': self.earnings_valuation.calculate_capitalized_earnings(),
            'earnings_power_value': self.earnings_valuation.calculate_earnings_power_value()
        }
    
    def _calculate_weighted_valuation(
        self,
        dcf_results: Dict[str, ValuationResult],
        relative_results: Dict[str, ValuationResult],
        asset_results: Dict[str, ValuationResult],
        earnings_results: Dict[str, ValuationResult]
    ) -> List[Dict[str, Any]]:
        """
        Calculate weighted valuation based on sector and applicability.
        
        Returns:
            List of weighted valuation methods
        """
        # Collect all applicable methods with base weights
        methods = []
        
        # DCF methods (higher weight for fundamental analysis)
        if not dcf_results['fcfe'].not_applicable:
            methods.append({
                'method': 'Free Cash Flow to Equity',
                'value': dcf_results['fcfe'].value_per_share,
                'base_weight': 0.25,
                'category': 'dcf'
            })
        
        if not dcf_results['fcff'].not_applicable:
            methods.append({
                'method': 'Free Cash Flow to Firm',
                'value': dcf_results['fcff'].value_per_share,
                'base_weight': 0.25,
                'category': 'dcf'
            })
        
        if not dcf_results['ddm'].not_applicable:
            methods.append({
                'method': 'Dividend Discount Model',
                'value': dcf_results['ddm'].value_per_share,
                'base_weight': 0.15,
                'category': 'dcf'
            })
        
        # Relative methods
        if not relative_results['pe'].not_applicable:
            methods.append({
                'method': 'P/E Ratio Valuation',
                'value': relative_results['pe'].value_per_share,
                'base_weight': 0.15,
                'category': 'relative'
            })
        
        if not relative_results['ev_ebitda'].not_applicable:
            methods.append({
                'method': 'EV/EBITDA Valuation',
                'value': relative_results['ev_ebitda'].value_per_share,
                'base_weight': 0.15,
                'category': 'relative'
            })
        
        # Asset methods (lower weight, more conservative)
        methods.append({
            'method': 'Book Value',
            'value': asset_results['book_value'].value_per_share,
            'base_weight': 0.05,
            'category': 'asset'
        })
        
        # Earnings methods
        if not earnings_results['capitalized_earnings'].not_applicable:
            methods.append({
                'method': 'Capitalized Earnings',
                'value': earnings_results['capitalized_earnings'].value_per_share,
                'base_weight': 0.10,
                'category': 'earnings'
            })
        
        if not earnings_results['earnings_power_value'].not_applicable:
            methods.append({
                'method': 'Earnings Power Value',
                'value': earnings_results['earnings_power_value'].value_per_share,
                'base_weight': 0.05,
                'category': 'earnings'
            })
        
        # Apply sector-specific adjustments
        adjusted_methods = self._apply_sector_adjustments(methods)
        
        # Normalize weights
        total_weight = sum(m['weight'] for m in adjusted_methods)
        for method in adjusted_methods:
            method['weight'] = method['weight'] / total_weight if total_weight > 0 else 0
        
        return adjusted_methods
    
    def _apply_sector_adjustments(self, methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply sector-specific weight adjustments."""
        sector = self.company_data.sector
        
        # Sector-specific weight multipliers
        sector_adjustments = {
            'Technology': {
                'dcf': 1.2,      # Higher weight on DCF for growth companies
                'relative': 1.1,
                'asset': 0.5,    # Lower weight on assets
                'earnings': 0.8  # Lower weight on static earnings
            },
            'Utilities': {
                'dcf': 1.0,
                'relative': 1.2,  # Higher weight on multiples for stable utilities
                'asset': 1.1,
                'earnings': 1.3   # Higher weight on stable earnings
            },
            'Real Estate': {
                'dcf': 0.9,
                'relative': 1.0,
                'asset': 1.5,     # Higher weight on asset values
                'earnings': 1.1
            },
            'Financials': {
                'dcf': 0.8,      # DCF less reliable for banks
                'relative': 1.3,  # P/E more important
                'asset': 1.2,    # Book value important
                'earnings': 1.1
            },
            'Energy': {
                'dcf': 1.1,
                'relative': 1.2,
                'asset': 1.0,
                'earnings': 0.7   # Cyclical earnings less reliable
            },
            'Healthcare': {
                'dcf': 1.1,
                'relative': 1.2,
                'asset': 0.8,
                'earnings': 1.0
            }
        }
        
        adjustments = sector_adjustments.get(sector, {
            'dcf': 1.0,
            'relative': 1.0,
            'asset': 1.0,
            'earnings': 1.0
        })
        
        # Apply adjustments
        for method in methods:
            category = method['category']
            multiplier = adjustments.get(category, 1.0)
            method['weight'] = method['base_weight'] * multiplier
        
        return methods
    
    def _calculate_final_value(self, weighted_valuations: List[Dict[str, Any]]) -> float:
        """
        Calculate final weighted intrinsic value.
        
        Args:
            weighted_valuations: List of weighted valuation methods
            
        Returns:
            Final intrinsic value per share
        """
        if not weighted_valuations:
            # Fallback to book value if no other methods available
            return self.asset_valuation.calculate_book_value().value_per_share
        
        # Calculate weighted average
        total_value = 0
        total_weight = 0
        
        for method in weighted_valuations:
            value = method['value']
            weight = method['weight']
            
            # Exclude extreme outliers (more than 5x or less than 0.2x median)
            median_value = self._calculate_median_value(weighted_valuations)
            if median_value > 0:
                if value > median_value * 5 or value < median_value * 0.2:
                    continue  # Skip outlier
            
            total_value += value * weight
            total_weight += weight
        
        return total_value / total_weight if total_weight > 0 else 0
    
    def _calculate_median_value(self, weighted_valuations: List[Dict[str, Any]]) -> float:
        """Calculate median value from all methods."""
        values = [method['value'] for method in weighted_valuations if method['value'] > 0]
        if not values:
            return 0
        
        values.sort()
        n = len(values)
        if n % 2 == 0:
            return (values[n // 2 - 1] + values[n // 2]) / 2
        else:
            return values[n // 2]
