"""Мутант FA_dict 02: отсутствующий переход считается отклонением.

Корректная partial DFA-семантика должна возвращать None, если переход
для пары состояние-вход не определен.
"""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    """
    Мутант FA_dict, нарушающий семантику отсутствующих переходов.
    """
    def accept_FA(self, word):
        """
        Возвращает отклонение вместо None при отсутствующем переходе.
        """
        state = self.initialState
        fired = []

        for symbol in word:
            key = self._lookup_key(state, symbol)
            if key is None:
                return False, fired
            fired.append(self._order.index(key))
            state = self.transitions[key]

        return self._is_final(state), fired
