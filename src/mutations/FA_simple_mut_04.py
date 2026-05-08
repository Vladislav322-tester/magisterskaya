"""
MUT-04
Нестабильная мутация.

Порядок кодирования состояний случайный.
"""

import random
from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def encode_states(self, *args, **kwargs):
        random.shuffle(self.transitionList)
        return super().encode_states(*args, **kwargs)
