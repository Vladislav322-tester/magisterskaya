"""
MUT-07
Поведенческая мутация.

accept_FA всегда возвращает False.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def accept_FA(self, word):
        return False
