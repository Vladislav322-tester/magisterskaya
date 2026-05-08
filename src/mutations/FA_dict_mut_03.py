"""FA_dict mutant: accept_FA starts from a non-initial state."""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def accept_FA(self, word):
        if not self.states:
            return False

        state = next(iter(self.states - {self.initialState}), self.initialState)
        for symbol in word:
            key = (state, symbol)
            if key not in self.transitions:
                return False
            state = self.transitions[key]
        return state in self.finalStates
