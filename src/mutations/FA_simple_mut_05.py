"""
MUT-05
Семантическая мутация.

Удаляются переходы с конкретным входом.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def encode_states(self, *args, **kwargs):
        # удаляем все переходы по 'a'
        self.transitionList = [
            t for t in self.transitionList
            if len(t) < 2 or t[1] != 'a'
        ]

        return super().encode_states(*args, **kwargs)
