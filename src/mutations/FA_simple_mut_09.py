"""
MUT-09: мутация полноты.

complete ничего не делает и оставляет автомат неполным.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, нарушающий дополнение автомата.
    """
    def complete(self):
        """
        Возвращает объект без добавления недостающих переходов.
        """
        return self
