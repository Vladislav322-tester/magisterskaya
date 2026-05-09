"""
MUT-03: семантическая мутация.

Переходы, связанные с начальным состоянием, удаляются перед кодированием.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, нарушающий кодирование состояний.
    """
    def encode_states(self, *args, **kwargs):
        # Удаляем переходы, связанные с initialState, перед кодированием.
        """
        Искажает transitionList перед вызовом исходного encode_states.
        """
        self.transitionList = [
            t for t in self.transitionList
            if t[0] != self.initialState and t[2] != self.initialState
        ]

        return super().encode_states(*args, **kwargs)
