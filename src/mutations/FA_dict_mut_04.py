"""
MUT-DICT-04
Нестабильная мутация.

Порядок переходов случайным образом изменяется.
"""

import random
from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):

    def build_transition_dict(self, *args, **kwargs):
        super().build_transition_dict(*args, **kwargs)

        for state in self.transitionDict:
            items = list(self.transitionDict[state].items())
            random.shuffle(items)
            self.transitionDict[state] = dict(items)