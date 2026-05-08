"""FA_dict mutant 04: encode_states forgets to update final states."""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def encode_states(self, is_abstraction=False, forced_transform=False):
        old_final_states = set(self.finalStates)
        result = super().encode_states(
            is_abstraction=is_abstraction,
            forced_transform=forced_transform,
        )
        self.finalStates = old_final_states
        return result
