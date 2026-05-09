"""
MUT-07: поведенческая мутация.

accept_FA всегда возвращает False вместо корректного результата.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, нарушающий семантику принятия.
    """
    def accept_FA(self, word):
        """
        Принудительно отклоняет любое входное слово.
        """
        return False
