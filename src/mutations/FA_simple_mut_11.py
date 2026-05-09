"""
MUT-11: структурная мутация.

is_complete всегда возвращает True.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, нарушающий проверку полноты.
    """
    def is_complete(self):
        """
        Сообщает, что любой автомат является полным.
        """
        return True
