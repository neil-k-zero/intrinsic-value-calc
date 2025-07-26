#!/usr/bin/env python3
"""
Data loading utilities for company financial data.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
import logging

# Import using absolute imports that work when run as script
try:
    from models.company_data import CompanyData
    from data.currency_converter import CurrencyConverter
    from data.standardized_assumptions import create_standardized_framework
except ImportError:
    # Fallback for when running as standalone script
    import sys
    sys.path.append('..')
from models.company_data import CompanyData
from data.data_validator import DataValidator
from data.currency_converter import CurrencyConverter
from data.standardized_assumptions import create_standardized_framework

logger = logging.getLogger(__name__)
class DataLoader:
    """
    Handles loading and initial processing of company data files.
    """
    
    def __init__(self, data_directory: Path, use_standardized_assumptions: bool = True):
        """
        Initialize DataLoader with data directory path.
        
        Args:
            data_directory: Path to directory containing company data files
            use_standardized_assumptions: Whether to apply standardized assumption framework
        """
        self.data_directory = data_directory
        self.use_standardized_assumptions = use_standardized_assumptions
        
        # Initialize standardization framework if enabled
        if self.use_standardized_assumptions:
            self.standardization_framework = create_standardized_framework()
            logger.info("🎯 DataLoader initialized with standardized assumption framework")
        else:
            self.standardization_framework = None
            logger.info("📊 DataLoader initialized without standardization (raw data mode)")
    
    def load_company_data(self, ticker: str) -> CompanyData:
        """
        Load company data from JSON file and convert to CompanyData object.
        
        Args:
            ticker: Company ticker symbol
            
        Returns:
            CompanyData object with normalized data and standardized assumptions
            
        Raises:
            FileNotFoundError: If company data file doesn't exist
            json.JSONDecodeError: If JSON file is invalid
            ValueError: If required data fields are missing
        """
        data_path = self.data_directory / f'{ticker.lower()}.json'
        
        if not data_path.exists():
            raise FileNotFoundError(f"Company data file not found: {data_path}")
        
        try:
            with open(data_path, 'r') as file:
                raw_data = json.load(file)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in {data_path}: {e}", e.doc, e.pos)
        
        # Convert currency if needed
        normalized_data = CurrencyConverter.convert_to_usd(raw_data)
        
        # Apply standardized assumptions if enabled
        if self.use_standardized_assumptions and self.standardization_framework:
            logger.info(f"🎯 Applying standardized assumptions to {ticker}")
            normalized_data = self.standardization_framework.apply_standardized_assumptions(normalized_data)
        else:
            logger.info(f"📊 Loading {ticker} with original assumptions")
        
        # Create and return CompanyData object
        return CompanyData.from_dict(normalized_data)
    
    def list_available_companies(self) -> list[Dict[str, str]]:
        """
        List all available company data files.
        
        Returns:
            List of dictionaries containing company information
        """
        if not self.data_directory.exists():
            return []
        
        companies = []
        json_files = list(self.data_directory.glob('*.json'))
        json_files = [f for f in json_files if f.name != 'template.json']
        
        for file_path in sorted(json_files):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                companies.append({
                    'ticker': data.get('ticker', 'N/A'),
                    'name': data.get('companyName', 'N/A'),
                    'sector': data.get('sector', 'N/A'),
                    'file': file_path.name
                })
            except (json.JSONDecodeError, KeyError):
                companies.append({
                    'ticker': file_path.stem.upper(),
                    'name': 'Invalid data file',
                    'sector': 'N/A',
                    'file': file_path.name
                })
        
        return companies
    
    @staticmethod
    def get_default_data_directory() -> Path:
        """
        Get the default data directory path relative to the current module.
        
        Returns:
            Path to the default data directory
        """
        current_dir = Path(__file__).parent
        return current_dir.parent.parent.parent / 'data'
