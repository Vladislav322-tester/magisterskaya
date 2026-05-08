"""
MUT-09
Completeness мутация.

complete() ничего не делает.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def complete(self):
        return self
