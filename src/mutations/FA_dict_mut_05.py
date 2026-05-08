"""FA_dict mutant: complete removes a transition instead of completing."""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def complete(self):
        if self.transitions:
            self.transitions.pop(next(iter(self.transitions)))
