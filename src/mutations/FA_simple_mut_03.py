"""
MUT-03
Семантическая мутация.

Начальное состояние исключается из кодирования.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def encode_states(self, *args, **kwargs):
        # удаляем initialState перед кодированием
        self.transitionList = [
            t for t in self.transitionList
            if t[0] != self.initialState and t[2] != self.initialState
        ]

        return super().encode_states(*args, **kwargs)
