"""
MUT-02
Структурная мутация.

Удаляется случайное состояние из списка состояний.
Менее тривиально, чем просто [-1].
"""

import random
from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def get_states_list(self):
        states = super().get_states_list()

        if len(states) > 1:
            idx = random.randint(0, len(states) - 1)
            return states[:idx] + states[idx+1:]

        return states
