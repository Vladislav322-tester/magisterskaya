"""
MUT-DICT-03
Семантическая мутация.

Игнорируется начальное состояние при выполнении автомата.
"""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):

    def accept(self, input_sequence):
        # стартуем не с initialState
        if not self.transitionDict:
            return False

        # берём случайное состояние
        current_state = list(self.transitionDict.keys())[0]

        for inp in input_sequence:
            current_state = self.transitionDict.get(current_state, {}).get(inp)

        return current_state in getattr(self, "finalStates", set())