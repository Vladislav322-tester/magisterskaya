"""Мутант FA_dict 03: поиск перехода игнорирует входной символ.

Такой мутант нарушает определение функции переходов delta(q, a).
"""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    """
    Мутант FA_dict, нарушающий поиск перехода.
    """
    def _lookup_key(self, state, symbol):
        """
        Ищет переход только по состоянию и игнорирует входной символ.
        """
        for key_state, key_symbol in self._order:
            if key_state == state:
                return (key_state, key_symbol)
        return None
