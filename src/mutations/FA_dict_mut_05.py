"""FA_dict mutant 05: complete() adds self-loops instead of a sink state."""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    def complete(self, comptype="loop", reaction=0):
        if comptype not in {"loop", "DCS"}:
            return None
        if comptype == "DCS" and not isinstance(reaction, int):
            return None

        states = self._all_states()
        inputs = self._all_inputs()
        self.states = set(states)
        self.inputs = set(inputs)

        for state in states:
            for symbol in inputs:
                if (state, symbol) not in self.transitions:
                    self._add_transition(
                        state,
                        symbol,
                        state,
                        reaction if self.isFSM else None,
                    )

        self._sync_declared_sizes()
        return reaction
