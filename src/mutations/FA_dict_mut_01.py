"""
MUT-DICT-01
Грубая логическая мутация.

Метод accept всегда возвращает False.
Контрольная мутация (easy-to-kill).
"""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):

    def accept(self, *args, **kwargs):
        return False