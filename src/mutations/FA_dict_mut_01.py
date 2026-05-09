"""Мутант FA_dict 01: неправильное условие принятия.

Автомат принимает слово тогда, когда корректная DFA-модель должна его
отклонить, и наоборот.
"""


from src.FA_dict import FA_dict as FA_dict_orig


class FA_dict(FA_dict_orig):
    """
    Мутант FA_dict, намеренно искажающий условие принятия DFA.
    """
    def accept_FA(self, word):
        """
        Инвертирует корректный результат принятия слова.
        """
        result = super().accept_FA(word)
        if result is None:
            return None
        accepted, fired = result
        return (not accepted), fired
