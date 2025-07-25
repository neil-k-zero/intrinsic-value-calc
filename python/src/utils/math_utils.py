#!/usr/bin/env python3
"""
Mathematical utility functions for financial calculations.
"""

from __future__ import annotations
import math
from typing import List, Optional, Union


class MathUtils:
    """
    Mathematical utility functions for financial calculations.
    """
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        Safely divide two numbers, returning default if division by zero.
        
        Args:
            numerator: Number to divide
            denominator: Number to divide by
            default: Default value if division by zero
            
        Returns:
            Result of division or default value
        """
        try:
            if denominator == 0:
                return default
            return numerator / denominator
        except (ZeroDivisionError, TypeError, ValueError):
            return default
    
    @staticmethod
    def safe_log(value: float, base: float = math.e) -> Optional[float]:
        """
        Safely calculate logarithm, returning None for invalid inputs.
        
        Args:
            value: Value to take logarithm of
            base: Base of logarithm (default: natural log)
            
        Returns:
            Logarithm result or None if invalid
        """
        try:
            if value <= 0 or base <= 0 or base == 1:
                return None
            return math.log(value) / math.log(base)
        except (ValueError, TypeError, ZeroDivisionError):
            return None
    
    @staticmethod
    def safe_power(base: float, exponent: float) -> Optional[float]:
        """
        Safely calculate power, handling edge cases.
        
        Args:
            base: Base number
            exponent: Exponent
            
        Returns:
            Power result or None if invalid
        """
        try:
            if base == 0 and exponent < 0:
                return None  # Division by zero
            if base < 0 and not isinstance(exponent, int):
                return None  # Complex result
            
            result = base ** exponent
            
            # Check for overflow/underflow
            if math.isinf(result) or math.isnan(result):
                return None
            
            return result
        except (ValueError, TypeError, OverflowError):
            return None
    
    @staticmethod
    def calculate_percentile(values: List[float], percentile: float) -> Optional[float]:
        """
        Calculate percentile of a list of values.
        
        Args:
            values: List of numeric values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value or None if invalid
        """
        try:
            if not values or percentile < 0 or percentile > 100:
                return None
            
            sorted_values = sorted([v for v in values if v is not None])
            if not sorted_values:
                return None
            
            if percentile == 0:
                return sorted_values[0]
            if percentile == 100:
                return sorted_values[-1]
            
            index = (percentile / 100) * (len(sorted_values) - 1)
            lower_index = int(index)
            upper_index = min(lower_index + 1, len(sorted_values) - 1)
            
            if lower_index == upper_index:
                return sorted_values[lower_index]
            
            # Linear interpolation
            weight = index - lower_index
            return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
            
        except (TypeError, ValueError, IndexError):
            return None
    
    @staticmethod
    def calculate_mean(values: List[float]) -> Optional[float]:
        """
        Calculate arithmetic mean of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Mean value or None if empty list
        """
        try:
            valid_values = [v for v in values if v is not None and not math.isnan(v)]
            if not valid_values:
                return None
            return sum(valid_values) / len(valid_values)
        except (TypeError, ValueError):
            return None
    
    @staticmethod
    def calculate_median(values: List[float]) -> Optional[float]:
        """
        Calculate median of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Median value or None if empty list
        """
        try:
            valid_values = sorted([v for v in values if v is not None and not math.isnan(v)])
            if not valid_values:
                return None
            
            n = len(valid_values)
            if n % 2 == 0:
                return (valid_values[n // 2 - 1] + valid_values[n // 2]) / 2
            else:
                return valid_values[n // 2]
        except (TypeError, ValueError, IndexError):
            return None
    
    @staticmethod
    def calculate_standard_deviation(values: List[float]) -> Optional[float]:
        """
        Calculate standard deviation of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Standard deviation or None if insufficient data
        """
        try:
            valid_values = [v for v in values if v is not None and not math.isnan(v)]
            if len(valid_values) < 2:
                return None
            
            mean = sum(valid_values) / len(valid_values)
            variance = sum((v - mean) ** 2 for v in valid_values) / (len(valid_values) - 1)
            return math.sqrt(variance)
        except (TypeError, ValueError):
            return None
    
    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """
        Clamp value between minimum and maximum bounds.
        
        Args:
            value: Value to clamp
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Clamped value
        """
        return max(min_value, min(max_value, value))
    
    @staticmethod
    def is_reasonable_number(value: Union[int, float], 
                           min_value: float = -1e12, 
                           max_value: float = 1e12) -> bool:
        """
        Check if a number is reasonable (not inf, nan, or extreme).
        
        Args:
            value: Number to check
            min_value: Minimum reasonable value
            max_value: Maximum reasonable value
            
        Returns:
            True if number is reasonable
        """
        try:
            if value is None:
                return False
            if math.isnan(value) or math.isinf(value):
                return False
            return min_value <= value <= max_value
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def compound_growth(initial_value: float, 
                       growth_rate: float, 
                       periods: int) -> Optional[float]:
        """
        Calculate compound growth.
        
        Args:
            initial_value: Starting value
            growth_rate: Growth rate per period (as decimal)
            periods: Number of periods
            
        Returns:
            Final value after compound growth
        """
        try:
            if initial_value <= 0 or periods < 0:
                return None
            
            result = initial_value * ((1 + growth_rate) ** periods)
            
            if not MathUtils.is_reasonable_number(result):
                return None
            
            return result
        except (ValueError, OverflowError):
            return None
    
    @staticmethod
    def present_value(future_value: float, 
                     discount_rate: float, 
                     periods: int) -> Optional[float]:
        """
        Calculate present value of future cash flow.
        
        Args:
            future_value: Future cash flow
            discount_rate: Discount rate per period (as decimal)
            periods: Number of periods
            
        Returns:
            Present value
        """
        try:
            if periods < 0 or discount_rate < -1:
                return None
            
            if discount_rate == 0:
                return future_value
            
            result = future_value / ((1 + discount_rate) ** periods)
            
            if not MathUtils.is_reasonable_number(result):
                return None
            
            return result
        except (ValueError, ZeroDivisionError, OverflowError):
            return None
