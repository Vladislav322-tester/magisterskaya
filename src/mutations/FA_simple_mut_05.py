"""
MUT-05: семантическая мутация.

Перед кодированием удаляются переходы с конкретным входным символом.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, удаляющий часть переходов перед кодированием.
    """
    def encode_states(self, *args, **kwargs):
        # Удаляем все переходы по входному символу 'a'.
        """
        Искажает автомат перед вызовом исходного encode_states.
        """
        self.transitionList = [
            t for t in self.transitionList
            if len(t) < 2 or t[1] != 'a'
        ]

        return super().encode_states(*args, **kwargs)
