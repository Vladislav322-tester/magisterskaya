"""
MUT-DICT-05
Семантическая мутация.

Один переход теряется после построения автомата.
"""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):

    def build_transition_dict(self, *args, **kwargs):
        super().build_transition_dict(*args, **kwargs)

        for state in self.transitionDict:
            if self.transitionDict[state]:
                key = next(iter(self.transitionDict[state]))
                del self.transitionDict[state][key]
                break