"""
MUT-04: нестабильная мутация.

Порядок переходов случайно перемешивается перед кодированием состояний.
"""

import random
from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, делающий кодирование состояний нестабильным.
    """
    def encode_states(self, *args, **kwargs):
        """
        Перемешивает transitionList перед кодированием.
        """
        random.shuffle(self.transitionList)
        return super().encode_states(*args, **kwargs)
