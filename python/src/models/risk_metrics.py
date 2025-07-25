#!/usr/bin/env python3
"""
RiskMetrics data model for risk assessment calculations.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class RiskMetrics:
    """
    Risk assessment metrics for company valuation.
    
    This class encapsulates all risk-related calculations and assessments
    used in the valuation process.
    """
    financial_risk: str
    business_risk: str
    valuation_risk: str
    
    # Financial metrics
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]
    interest_coverage: Optional[float]
    
    # Business metrics
    beta: float
    industry_risk: str
    volatility_risk: str
    
    # Valuation metrics
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization."""
        return {
            'financial': {
                'riskLevel': self.financial_risk,
                'debtToEquity': self.debt_to_equity,
                'currentRatio': self.current_ratio,
                'interestCoverage': self.interest_coverage
            },
            'business': {
                'volatilityRisk': self.volatility_risk,
                'beta': self.beta,
                'industryRisk': self.industry_risk
            },
            'valuation': {
                'valuationRisk': self.valuation_risk,
                'peRatio': self.pe_ratio,
                'pbRatio': self.pb_ratio
            }
        }
    
    @classmethod
    def create_from_calculations(
        cls,
        debt_to_equity: Optional[float],
        current_ratio: Optional[float],
        interest_coverage: Optional[float],
        beta: float,
        pe_ratio: Optional[float],
        pb_ratio: Optional[float],
        sector: str
    ) -> RiskMetrics:
        """
        Create RiskMetrics from calculated values.
        
        Args:
            debt_to_equity: Debt to equity ratio
            current_ratio: Current ratio
            interest_coverage: Interest coverage ratio
            beta: Beta coefficient
            pe_ratio: Price to earnings ratio
            pb_ratio: Price to book ratio
            sector: Company sector
            
        Returns:
            RiskMetrics instance with calculated risk levels
        """
        # Calculate financial risk level
        financial_risk = cls._assess_financial_risk(debt_to_equity, current_ratio, interest_coverage)
        
        # Calculate business risk level
        volatility_risk = cls._assess_volatility_risk(beta)
        industry_risk = cls._assess_industry_risk(sector)
        business_risk = max(volatility_risk, industry_risk, key=lambda x: ['Low', 'Medium', 'High'].index(x))
        
        # Calculate valuation risk level
        valuation_risk = cls._assess_valuation_risk(pe_ratio, pb_ratio)
        
        return cls(
            financial_risk=financial_risk,
            business_risk=business_risk,
            valuation_risk=valuation_risk,
            debt_to_equity=debt_to_equity,
            current_ratio=current_ratio,
            interest_coverage=interest_coverage,
            beta=beta,
            industry_risk=industry_risk,
            volatility_risk=volatility_risk,
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio
        )
    
    @staticmethod
    def _assess_financial_risk(
        debt_to_equity: Optional[float],
        current_ratio: Optional[float],
        interest_coverage: Optional[float]
    ) -> str:
        """Assess financial risk level based on ratios."""
        risk_score = 0
        
        # Debt to equity assessment
        if debt_to_equity is None:
            risk_score += 3  # Negative equity is high risk
        elif debt_to_equity > 2.0:
            risk_score += 3
        elif debt_to_equity > 1.0:
            risk_score += 2
        elif debt_to_equity > 0.5:
            risk_score += 1
        
        # Current ratio assessment
        if current_ratio is not None:
            if current_ratio < 1.0:
                risk_score += 2
            elif current_ratio < 1.5:
                risk_score += 1
        
        # Interest coverage assessment
        if interest_coverage is not None:
            if interest_coverage < 2.0:
                risk_score += 3
            elif interest_coverage < 5.0:
                risk_score += 2
            elif interest_coverage < 10.0:
                risk_score += 1
        
        if risk_score >= 5:
            return "High"
        elif risk_score >= 3:
            return "Medium"
        else:
            return "Low"
    
    @staticmethod
    def _assess_volatility_risk(beta: float) -> str:
        """Assess volatility risk based on beta."""
        if beta > 1.5:
            return "High"
        elif beta > 1.2:
            return "Medium"
        else:
            return "Low"
    
    @staticmethod
    def _assess_industry_risk(sector: str) -> str:
        """Assess industry risk based on sector."""
        high_risk_sectors = ['Technology', 'Biotechnology', 'Energy', 'Materials']
        medium_risk_sectors = ['Healthcare', 'Industrials', 'Communication Services']
        
        if sector in high_risk_sectors:
            return "High"
        elif sector in medium_risk_sectors:
            return "Medium"
        else:
            return "Low"
    
    @staticmethod
    def _assess_valuation_risk(pe_ratio: Optional[float], pb_ratio: Optional[float]) -> str:
        """Assess valuation risk based on multiples."""
        risk_score = 0
        
        if pe_ratio is not None:
            if pe_ratio > 30:
                risk_score += 2
            elif pe_ratio > 20:
                risk_score += 1
            elif pe_ratio < 5:
                risk_score += 1  # Suspiciously low P/E can indicate problems
        
        if pb_ratio is not None:
            if pb_ratio > 5:
                risk_score += 2
            elif pb_ratio > 3:
                risk_score += 1
            elif pb_ratio < 0.5:
                risk_score += 1  # Very low P/B might indicate distress
        
        if risk_score >= 3:
            return "High"
        elif risk_score >= 1:
            return "Medium"
        else:
            return "Low"
