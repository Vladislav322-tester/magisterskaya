"""FA_dict mutant 01: wrong acceptance condition.

The automaton accepts exactly when the final state is not accepting.
"""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def accept_FA(self, word):
        result = super().accept_FA(word)
        if result is None:
            return None
        accepted, fired = result
        return (not accepted), fired
