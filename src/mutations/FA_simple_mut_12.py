"""
MUT-12: FSM-мутация.

Выходные символы игнорируются.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, нарушающий множество выходов FSM.
    """
    def get_outputs_list(self):
        """
        Возвращает пустой список выходов.
        """
        return []
