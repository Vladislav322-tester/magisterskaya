"""FA_dict mutant 03: transition lookup ignores the input symbol."""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def _lookup_key(self, state, symbol):
        for key_state, key_symbol in self._order:
            if key_state == state:
                return (key_state, key_symbol)
        return None
