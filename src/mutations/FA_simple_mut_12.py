"""
MUT-12
FSM мутация.

Выходы игнорируются.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def get_outputs_list(self):
        return []
