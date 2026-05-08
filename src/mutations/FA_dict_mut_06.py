"""FA_dict mutant: is_complete always returns true."""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def is_complete(self):
        return True
