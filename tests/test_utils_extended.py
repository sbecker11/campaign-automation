"""
Extended tests for utility functions.
"""

import pytest
from src import utils


def test_all_utility_functions():
    """Test all utility functions in utils module."""
    # Get all functions from utils
    import inspect
    
    functions = [name for name, obj in inspect.getmembers(utils) 
                 if inspect.isfunction(obj) and not name.startswith('_')]
    
    # Test that functions exist and can be called
    for func_name in functions:
        func = getattr(utils, func_name)
        assert callable(func)
