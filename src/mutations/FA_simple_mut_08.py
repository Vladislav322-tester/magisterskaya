"""
MUT-08
Поведенческая мутация.

accept_FA игнорирует последний символ входа.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def accept_FA(self, word):
        if word:
            word = word[:-1]
        return super().accept_FA(word)
