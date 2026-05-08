"""
MUT-DICT-02
Структурная мутация.

Удаляется одно состояние из множества состояний.
"""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):

    def get_states_list(self):
        states = super().get_states_list()
        if states:
            return states[:-1]
        return states