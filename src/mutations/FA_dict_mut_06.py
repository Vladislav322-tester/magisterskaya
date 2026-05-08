"""
MUT-DICT-06
Нарушение идемпотентности.

Повторное построение переходов изменяет автомат.
"""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):

    def build_transition_dict(self, *args, **kwargs):
        super().build_transition_dict(*args, **kwargs)

        # повторное "искажение"
        for state in list(self.transitionDict.keys()):
            self.transitionDict[f"x_{state}"] = self.transitionDict.pop(state)