"""
Моки для тестирования.
"""

from .mock_efa import MockEFA, MockEFAComplex
from .mock_fa import MockFA, MockFADeterministic, MockFANonDeterministic

__all__ = [
    "MockEFA",
    "MockEFAComplex",
    "MockFA",
    "MockFADeterministic",
    "MockFANonDeterministic",
]