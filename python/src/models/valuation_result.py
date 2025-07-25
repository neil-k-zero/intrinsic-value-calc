#!/usr/bin/env python3
"""
ValuationResult data model for storing valuation method results.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ValuationResult:
    """
    Dataclass for individual valuation method results.
    
    Attributes:
        method: Name of the valuation method
        value_per_share: Calculated value per share
        upside: Percentage upside vs current price
        assumptions: Key calculation assumptions
        not_applicable: Whether this method is applicable
        reason: Explanation if method not applicable
    """
    method: str
    value_per_share: float
    upside: float
    assumptions: Dict[str, Any]
    not_applicable: bool = False
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization."""
        result = {
            'method': self.method,
            'valuePerShare': self.value_per_share,
            'upside': self.upside,
            'assumptions': self.assumptions,
            'notApplicable': self.not_applicable
        }
        
        if self.reason:
            result['reason'] = self.reason
            
        return result
    
    @classmethod
    def create_not_applicable(cls, method: str, reason: str, discount_rate: float = 0.0) -> ValuationResult:
        """
        Create a ValuationResult for non-applicable methods.
        
        Args:
            method: Name of the valuation method
            reason: Reason why the method is not applicable
            discount_rate: Discount rate used (if applicable)
            
        Returns:
            ValuationResult instance marked as not applicable
        """
        return cls(
            method=method,
            value_per_share=0,
            upside=0,
            assumptions={'discountRate': discount_rate} if discount_rate > 0 else {},
            not_applicable=True,
            reason=reason
        )
