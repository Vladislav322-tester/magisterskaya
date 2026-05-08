"""FA_dict mutant: accept_FA always rejects."""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def accept_FA(self, word):
        return False
