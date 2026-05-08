"""
MUT-11
Структурная мутация.

is_complete всегда возвращает True.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def is_complete(self):
        return True
