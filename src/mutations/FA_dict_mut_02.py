"""FA_dict mutant 02: missing transitions reject instead of returning None."""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def accept_FA(self, word):
        state = self.initialState
        fired = []

        for symbol in word:
            key = self._lookup_key(state, symbol)
            if key is None:
                return False, fired
            fired.append(self._order.index(key))
            state = self.transitions[key]

        return self._is_final(state), fired
