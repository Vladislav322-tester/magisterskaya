"""
MUT-01
Грубая логическая мутация.

__eq__ всегда возвращает False.
Контрольная мутация (easy-to-kill).
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def __eq__(self, other):
        return False
