"""Мутант FA_dict 04: encode_states не обновляет допускающие состояния.

Мутант нарушает сохранение языка при переименовании состояний.
"""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    """
    Мутант FA_dict, нарушающий сохранение допускающих состояний.
    """
    def encode_states(self, is_abstraction=False, forced_transform=False):
        """
        Выполняет кодирование, но возвращает старое множество finalStates.
        """
        old_final_states = set(self.finalStates)
        result = super().encode_states(
            is_abstraction=is_abstraction,
            forced_transform=forced_transform,
        )
        self.finalStates = old_final_states
        return result
