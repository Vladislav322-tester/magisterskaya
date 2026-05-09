"""Мутант FA_dict 06: is_complete игнорирует часть входного алфавита.

Корректная проверка полноты должна учитывать каждую пару Q x Sigma.
"""

from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    """
    Мутант FA_dict, нарушающий проверку полноты автомата.
    """
    def is_complete(self):
        """
        Проверяет только первый входной символ вместо всего алфавита.
        """
        inputs = self._all_inputs()
        if not inputs:
            return True
        first_input = next(iter(inputs))
        return all((state, first_input) in self.transitions for state in self._all_states())
