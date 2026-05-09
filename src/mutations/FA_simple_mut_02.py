"""
MUT-02: структурная мутация.

Из списка состояний удаляется случайное состояние. Мутант проверяет,
замечают ли тесты потерю элемента множества Q.
"""

import random
from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, намеренно искажающий список состояний.
    """
    def get_states_list(self):
        """
        Возвращает список состояний с удаленным случайным элементом.
        """
        states = super().get_states_list()

        if len(states) > 1:
            idx = random.randint(0, len(states) - 1)
            return states[:idx] + states[idx+1:]

        return states
