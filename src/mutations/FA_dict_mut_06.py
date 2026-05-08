"""FA_dict mutant 06: is_complete checks states but ignores inputs."""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def is_complete(self):
        inputs = self._all_inputs()
        if not inputs:
            return True
        first_input = next(iter(inputs))
        return all((state, first_input) in self.transitions for state in self._all_states())
