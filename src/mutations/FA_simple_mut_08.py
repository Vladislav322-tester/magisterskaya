"""
MUT-08: поведенческая мутация.

accept_FA игнорирует последний символ входного слова.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, нарушающий обработку входного слова.
    """
    def accept_FA(self, word):
        """
        Удаляет последний символ слова перед запуском исходного accept_FA.
        """
        if word:
            word = word[:-1]
        return super().accept_FA(word)
