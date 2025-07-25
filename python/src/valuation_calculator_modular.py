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
        Calculate weighted valuation based on sector, applicability, and confidence.
        
        Returns:
            List of weighted valuation methods with transparency data
        """
        # Collect all applicable methods with base weights
        methods = []
        
        # DCF methods (higher weight for fundamental analysis)
        if not dcf_results['fcfe'].not_applicable:
            methods.append({
                'method': 'Free Cash Flow to Equity',
                'value': dcf_results['fcfe'].value_per_share,
                'base_weight': 0.25,
                'category': 'dcf',
                'result_object': dcf_results['fcfe']
            })
        
        if not dcf_results['fcff'].not_applicable:
            methods.append({
                'method': 'Free Cash Flow to Firm',
                'value': dcf_results['fcff'].value_per_share,
                'base_weight': 0.25,
                'category': 'dcf',
                'result_object': dcf_results['fcff']
            })
        
        if not dcf_results['ddm'].not_applicable:
            methods.append({
                'method': 'Dividend Discount Model',
                'value': dcf_results['ddm'].value_per_share,
                'base_weight': 0.15,
                'category': 'dcf',
                'result_object': dcf_results['ddm']
            })
        
        # Relative methods
        if not relative_results['pe'].not_applicable:
            methods.append({
                'method': 'P/E Ratio Valuation',
                'value': relative_results['pe'].value_per_share,
                'base_weight': 0.15,
                'category': 'relative',
                'result_object': relative_results['pe']
            })
        
        if not relative_results['ev_ebitda'].not_applicable:
            methods.append({
                'method': 'EV/EBITDA Valuation',
                'value': relative_results['ev_ebitda'].value_per_share,
                'base_weight': 0.15,
                'category': 'relative',
                'result_object': relative_results['ev_ebitda']
            })
        
        # Asset methods (lower weight, more conservative)
        methods.append({
            'method': 'Book Value',
            'value': asset_results['book_value'].value_per_share,
            'base_weight': 0.05,
            'category': 'asset',
            'result_object': asset_results['book_value']
        })
        
        # Earnings methods
        if not earnings_results['capitalized_earnings'].not_applicable:
            methods.append({
                'method': 'Capitalized Earnings',
                'value': earnings_results['capitalized_earnings'].value_per_share,
                'base_weight': 0.10,
                'category': 'earnings',
                'result_object': earnings_results['capitalized_earnings']
            })
        
        if not earnings_results['earnings_power_value'].not_applicable:
            methods.append({
                'method': 'Earnings Power Value',
                'value': earnings_results['earnings_power_value'].value_per_share,
                'base_weight': 0.05,
                'category': 'earnings',
                'result_object': earnings_results['earnings_power_value']
            })
        
        # Calculate confidence-based adjustments
        confidence_adjustments = self._calculate_confidence_adjustments(methods)
        
        # Apply sector-specific adjustments
        sector_adjusted_methods = self._apply_sector_adjustments(methods)
        
        # Apply confidence adjustments
        final_methods = self._apply_confidence_adjustments(sector_adjusted_methods, confidence_adjustments)
        
        # Apply outlier handling with down-weighting instead of exclusion
        final_methods = self._handle_outliers_with_downweighting(final_methods)
        
        # Normalize weights
        total_weight = sum(m['final_weight'] for m in final_methods)
        for method in final_methods:
            method['normalized_weight'] = method['final_weight'] / total_weight if total_weight > 0 else 0
        
        return final_methods
    
    def _calculate_confidence_adjustments(self, methods: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate confidence-based weight adjustments based on result variance.
        
        Args:
            methods: List of valuation methods
            
        Returns:
            Dictionary of category adjustments based on confidence
        """
        # Group methods by category
        categories = {}
        for method in methods:
            category = method['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(method['value'])
        
        # Calculate variance for each category
        category_adjustments = {}
        
        for category, values in categories.items():
            if len(values) < 2:
                # Single method - neutral adjustment
                category_adjustments[category] = 1.0
                continue
            
            # Calculate coefficient of variation (CV) as measure of confidence
            mean_value = sum(values) / len(values)
            if mean_value == 0:
                category_adjustments[category] = 0.5  # Very low confidence
                continue
            
            variance = sum((v - mean_value) ** 2 for v in values) / len(values)
            std_dev = variance ** 0.5
            cv = std_dev / mean_value
            
            # Convert CV to confidence adjustment
            # Lower CV = higher confidence = higher weight
            if cv <= 0.1:  # Very low variance - high confidence
                category_adjustments[category] = 1.2
            elif cv <= 0.2:  # Low variance - good confidence
                category_adjustments[category] = 1.1
            elif cv <= 0.4:  # Moderate variance - neutral
                category_adjustments[category] = 1.0
            elif cv <= 0.6:  # High variance - lower confidence
                category_adjustments[category] = 0.8
            else:  # Very high variance - low confidence
                category_adjustments[category] = 0.6
        
        return category_adjustments
    
    def _apply_confidence_adjustments(
        self, 
        methods: List[Dict[str, Any]], 
        confidence_adjustments: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Apply confidence-based adjustments to method weights.
        
        Args:
            methods: List of methods with sector adjustments
            confidence_adjustments: Category-based confidence adjustments
            
        Returns:
            Methods with confidence adjustments applied
        """
        for method in methods:
            category = method['category']
            confidence_multiplier = confidence_adjustments.get(category, 1.0)
            
            # Store intermediate values for transparency
            method['confidence_adjustment'] = confidence_multiplier
            method['final_weight'] = method['weight'] * confidence_multiplier
        
        return methods
    
    def _handle_outliers_with_downweighting(self, methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Handle outliers by down-weighting instead of exclusion.
        
        Args:
            methods: List of valuation methods
            
        Returns:
            Methods with outlier adjustments applied
        """
        if len(methods) < 3:
            # Not enough methods to identify outliers reliably
            for method in methods:
                method['outlier_adjustment'] = 1.0
            return methods
        
        # Calculate median value
        values = [method['value'] for method in methods if method['value'] > 0]
        if not values:
            return methods
        
        values.sort()
        n = len(values)
        median_value = values[n // 2] if n % 2 == 1 else (values[n // 2 - 1] + values[n // 2]) / 2
        
        if median_value <= 0:
            return methods
        
        # Apply graduated outlier adjustments
        for method in methods:
            value = method['value']
            ratio = value / median_value if median_value > 0 else 1.0
            
            # Graduated down-weighting for outliers
            if ratio > 5.0:  # Extreme high outlier
                method['outlier_adjustment'] = 0.1
                method['outlier_reason'] = f"Extreme high outlier ({ratio:.1f}x median)"
            elif ratio > 3.0:  # High outlier
                method['outlier_adjustment'] = 0.3
                method['outlier_reason'] = f"High outlier ({ratio:.1f}x median)"
            elif ratio > 2.0:  # Moderate high outlier
                method['outlier_adjustment'] = 0.6
                method['outlier_reason'] = f"Moderate high outlier ({ratio:.1f}x median)"
            elif ratio < 0.2:  # Extreme low outlier
                method['outlier_adjustment'] = 0.1
                method['outlier_reason'] = f"Extreme low outlier ({ratio:.1f}x median)"
            elif ratio < 0.33:  # Low outlier
                method['outlier_adjustment'] = 0.3
                method['outlier_reason'] = f"Low outlier ({ratio:.1f}x median)"
            elif ratio < 0.5:  # Moderate low outlier
                method['outlier_adjustment'] = 0.6
                method['outlier_reason'] = f"Moderate low outlier ({ratio:.1f}x median)"
            else:  # Normal range
                method['outlier_adjustment'] = 1.0
                method['outlier_reason'] = "Within normal range"
            
            # Apply outlier adjustment to final weight
            method['final_weight'] = method['final_weight'] * method['outlier_adjustment']
        
        return methods
    
    def _apply_sector_adjustments(self, methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply enhanced sector-specific weight adjustments."""
        sector = self.company_data.sector
        
        # Base sector-specific weight multipliers
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
        
        # Get base adjustments for sector
        adjustments = sector_adjustments.get(sector, {
            'dcf': 1.0,
            'relative': 1.0,
            'asset': 1.0,
            'earnings': 1.0
        })
        
        # Apply enhanced Healthcare-specific adjustments
        if sector == 'Healthcare':
            adjustments = self._apply_healthcare_specific_adjustments(adjustments)
        
        # Apply adjustments and store transparency data
        for method in methods:
            category = method['category']
            multiplier = adjustments.get(category, 1.0)
            
            # Store adjustment details for transparency
            method['sector_adjustment'] = multiplier
            method['sector'] = sector
            method['weight'] = method['base_weight'] * multiplier
        
        return methods
    
    def _apply_healthcare_specific_adjustments(self, base_adjustments: Dict[str, float]) -> Dict[str, float]:
        """
        Apply healthcare-specific granular adjustments.
        
        For companies like Novo Nordisk with strong fundamentals and growth prospects,
        adjust weights based on company characteristics.
        """
        adjusted = base_adjustments.copy()
        
        try:
            # Check for strong R&D pipeline indicators
            revenue_growth = self._get_revenue_growth_rate()
            profit_margins = self._get_profit_margins()
            roe = self._get_roe()
            
            # For high-quality healthcare companies with strong growth
            if (revenue_growth > 0.10 and  # >10% revenue growth
                profit_margins > 0.30 and   # >30% profit margins
                roe > 0.25):                # >25% ROE
                
                # Increase P/E weight for high-quality growth companies
                adjusted['relative'] *= 1.3
                # Slightly increase DCF weight for sustainable growth
                adjusted['dcf'] *= 1.15
                # Reduce asset-based weight (less relevant for IP-heavy companies)
                adjusted['asset'] *= 0.6
            
            # For dividend-paying healthcare companies with stable cash flows
            dividend_yield = self.company_data.raw_data.get('dividendInfo', {}).get('currentDividendYield', 0)
            if dividend_yield > 0.015:  # >1.5% dividend yield
                # Increase earnings-based methods weight
                adjusted['earnings'] *= 1.2
                # Maintain DCF weight for dividend sustainability analysis
                adjusted['dcf'] *= 1.1
            
        except Exception:
            # If data is missing, use base adjustments
            pass
        
        return adjusted
    
    def _get_revenue_growth_rate(self) -> float:
        """Calculate recent revenue growth rate."""
        try:
            revenue_data = self.company_data.get_financial_series('revenue', 3)
            values = list(revenue_data.values())
            if len(values) >= 2:
                recent = values[0]  # Most recent
                prior = values[-1]  # Oldest
                years = len(values) - 1
                return (recent / prior) ** (1 / years) - 1 if prior > 0 else 0
        except Exception:
            pass
        return 0.0
    
    def _get_profit_margins(self) -> float:
        """Calculate current profit margins."""
        try:
            revenue = self.company_data.get_latest_financial_data('revenue')
            net_income = self.company_data.get_latest_financial_data('netIncome')
            return net_income / revenue if revenue > 0 else 0
        except Exception:
            return 0.0
    
    def _get_roe(self) -> float:
        """Calculate return on equity."""
        try:
            net_income = self.company_data.get_latest_financial_data('netIncome')
            equity = self.company_data.get_latest_financial_data('shareholderEquity')
            return net_income / equity if equity > 0 else 0
        except Exception:
            return 0.0
    
    def _calculate_final_value(self, weighted_valuations: List[Dict[str, Any]]) -> float:
        """
        Calculate final weighted intrinsic value using enhanced methodology.
        
        Args:
            weighted_valuations: List of weighted valuation methods with transparency data
            
        Returns:
            Final intrinsic value per share
        """
        if not weighted_valuations:
            # Fallback to book value if no other methods available
            return self.asset_valuation.calculate_book_value().value_per_share
        
        # Calculate weighted average using normalized weights
        total_value = 0
        total_weight = 0
        
        for method in weighted_valuations:
            value = method['value']
            weight = method['normalized_weight']
            
            # All outlier handling is now done in preprocessing
            # Just use the normalized weights directly
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
