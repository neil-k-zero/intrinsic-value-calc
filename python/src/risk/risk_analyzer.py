#!/usr/bin/env python3
"""
Risk analysis for company valuation.
"""

from __future__ import annotations
from typing import Dict, Any

from models.company_data import CompanyData
from models.risk_metrics import RiskMetrics
from utils.financial_calculations import FinancialCalculations


class RiskAnalyzer:
    """
    Analyzes various risk factors for company valuation.
    
    This class calculates financial, business, and valuation risk metrics
    to provide comprehensive risk assessment.
    """
    
    def __init__(self, company_data: CompanyData):
        """
        Initialize risk analyzer.
        
        Args:
            company_data: Normalized company data
        """
        self.company_data = company_data
        self.calc = FinancialCalculations(company_data)
    
    def analyze_all_risks(self) -> RiskMetrics:
        """
        Perform comprehensive risk analysis.
        
        Returns:
            RiskMetrics object with all risk assessments
        """
        # Calculate financial ratios
        debt_to_equity = self.calc.calculate_debt_to_equity()
        current_ratio = self.calc.calculate_current_ratio()
        interest_coverage = self.calc.calculate_interest_coverage()
        
        # Get market data
        beta = self.company_data.market_data.get('beta', 1.0)
        
        # Calculate valuation ratios
        pe_ratio = self._calculate_pe_ratio()
        pb_ratio = self._calculate_pb_ratio()
        
        # Create risk metrics
        return RiskMetrics.create_from_calculations(
            debt_to_equity=debt_to_equity,
            current_ratio=current_ratio,
            interest_coverage=interest_coverage,
            beta=beta,
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio,
            sector=self.company_data.sector
        )
    
    def calculate_financial_risk_score(self) -> float:
        """
        Calculate quantitative financial risk score (0-100).
        
        Returns:
            Risk score where higher values indicate higher risk
        """
        score = 0.0
        
        # Debt to equity (25% weight)
        debt_to_equity = self.calc.calculate_debt_to_equity()
        if debt_to_equity is None:
            score += 25  # Negative equity is maximum risk
        elif debt_to_equity > 2.0:
            score += 25
        elif debt_to_equity > 1.0:
            score += 15
        elif debt_to_equity > 0.5:
            score += 8
        
        # Current ratio (20% weight)
        current_ratio = self.calc.calculate_current_ratio()
        if current_ratio is not None:
            if current_ratio < 1.0:
                score += 20
            elif current_ratio < 1.5:
                score += 10
            elif current_ratio < 2.0:
                score += 5
        
        # Interest coverage (25% weight)
        interest_coverage = self.calc.calculate_interest_coverage()
        if interest_coverage is not None:
            if interest_coverage < 2.0:
                score += 25
            elif interest_coverage < 5.0:
                score += 15
            elif interest_coverage < 10.0:
                score += 8
        
        # Profitability (15% weight)
        roe = self.calc.calculate_roe()
        if roe < 0:
            score += 15
        elif roe < 0.05:
            score += 10
        elif roe < 0.10:
            score += 5
        
        # Revenue stability (15% weight)
        revenue_volatility = self._calculate_revenue_volatility()
        if revenue_volatility > 0.30:
            score += 15
        elif revenue_volatility > 0.15:
            score += 10
        elif revenue_volatility > 0.10:
            score += 5
        
        return min(100, score)
    
    def calculate_business_risk_score(self) -> float:
        """
        Calculate business risk score (0-100).
        
        Returns:
            Risk score where higher values indicate higher risk
        """
        score = 0.0
        
        # Beta (40% weight)
        beta = self.company_data.market_data.get('beta', 1.0)
        if beta > 2.0:
            score += 40
        elif beta > 1.5:
            score += 30
        elif beta > 1.2:
            score += 20
        elif beta > 1.0:
            score += 10
        
        # Sector risk (35% weight)
        sector_risk = self._get_sector_risk_score(self.company_data.sector)
        score += sector_risk * 0.35
        
        # Company size (market cap) - 25% weight
        market_cap = self.company_data.get_market_cap()
        if market_cap < 1000:  # < $1B
            score += 25
        elif market_cap < 5000:  # < $5B
            score += 15
        elif market_cap < 20000:  # < $20B
            score += 8
        
        return min(100, score)
    
    def calculate_valuation_risk_score(self) -> float:
        """
        Calculate valuation risk score (0-100).
        
        Returns:
            Risk score where higher values indicate higher risk
        """
        score = 0.0
        
        # P/E ratio (40% weight)
        pe_ratio = self._calculate_pe_ratio()
        if pe_ratio is not None:
            if pe_ratio > 40:
                score += 40
            elif pe_ratio > 25:
                score += 30
            elif pe_ratio > 20:
                score += 20
            elif pe_ratio > 15:
                score += 10
            elif pe_ratio < 5:
                score += 15  # Suspiciously low
        
        # P/B ratio (30% weight)
        pb_ratio = self._calculate_pb_ratio()
        if pb_ratio is not None:
            if pb_ratio > 8:
                score += 30
            elif pb_ratio > 5:
                score += 20
            elif pb_ratio > 3:
                score += 10
            elif pb_ratio < 0.5:
                score += 15  # Potential distress
        
        # Price to sales (30% weight)
        ps_ratio = self._calculate_ps_ratio()
        if ps_ratio is not None:
            if ps_ratio > 10:
                score += 30
            elif ps_ratio > 5:
                score += 20
            elif ps_ratio > 3:
                score += 10
        
        return min(100, score)
    
    def _calculate_pe_ratio(self) -> float:
        """Calculate price to earnings ratio."""
        try:
            current_price = self.company_data.get_current_price()
            net_income = self.company_data.get_latest_financial_data('netIncome')
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            if net_income <= 0:
                return None
            
            eps = net_income / shares_outstanding
            return current_price / eps
        except Exception:
            return None
    
    def _calculate_pb_ratio(self) -> float:
        """Calculate price to book ratio."""
        try:
            current_price = self.company_data.get_current_price()
            shareholder_equity = self.company_data.get_latest_financial_data('shareholderEquity')
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            if shareholder_equity <= 0:
                return None
            
            book_value_per_share = shareholder_equity / shares_outstanding
            return current_price / book_value_per_share
        except Exception:
            return None
    
    def _calculate_ps_ratio(self) -> float:
        """Calculate price to sales ratio."""
        try:
            current_price = self.company_data.get_current_price()
            revenue = self.company_data.get_latest_financial_data('revenue')
            shares_outstanding = self.company_data.get_shares_outstanding()
            
            if revenue <= 0:
                return None
            
            sales_per_share = revenue / shares_outstanding
            return current_price / sales_per_share
        except Exception:
            return None
    
    def _calculate_revenue_volatility(self) -> float:
        """Calculate revenue volatility over time."""
        try:
            revenue_data = self.company_data.get_financial_series('revenue', 5)
            revenues = list(revenue_data.values())
            
            if len(revenues) < 3:
                return 0.5  # High volatility if insufficient data
            
            # Calculate coefficient of variation
            mean_revenue = sum(revenues) / len(revenues)
            variance = sum((r - mean_revenue) ** 2 for r in revenues) / len(revenues)
            std_dev = variance ** 0.5
            
            if mean_revenue == 0:
                return 1.0
            
            return std_dev / mean_revenue
        except Exception:
            return 0.5
    
    def _get_sector_risk_score(self, sector: str) -> float:
        """
        Get risk score for sector (0-100).
        
        Args:
            sector: Company sector
            
        Returns:
            Sector risk score
        """
        sector_risks = {
            'Technology': 70,
            'Biotechnology': 85,
            'Energy': 75,
            'Materials': 65,
            'Healthcare': 45,
            'Industrials': 55,
            'Communication Services': 60,
            'Consumer Discretionary': 60,
            'Consumer Staples': 30,
            'Utilities': 25,
            'Real Estate': 50,
            'Financials': 65
        }
        
        return sector_risks.get(sector, 55)  # Default medium risk
