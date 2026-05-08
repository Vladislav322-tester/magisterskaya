"""
MUT-06
Нарушение идемпотентности.

Каждый вызов encode_states добавляет новые переходы.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def encode_states(self, *args, **kwargs):
        super().encode_states(*args, **kwargs)

        if self.transitionList:
            t = self.transitionList[0]
            self.transitionList.append(t)

        return self
