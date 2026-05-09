"""
MUT-06: нарушение идемпотентности.

Каждый вызов encode_states добавляет дубликат перехода.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, нарушающий идемпотентность кодирования.
    """
    def encode_states(self, *args, **kwargs):
        """
        Добавляет дубликат первого перехода после кодирования.
        """
        super().encode_states(*args, **kwargs)

        if self.transitionList:
            t = self.transitionList[0]
            self.transitionList.append(t)

        return self
