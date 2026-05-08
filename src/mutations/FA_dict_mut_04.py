"""FA_dict mutant: encode_states is a no-op."""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def encode_states(self, forced_transform=False):
        return None
