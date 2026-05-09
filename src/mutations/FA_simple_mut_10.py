"""
MUT-10: мутация полноты.

complete удаляет переходы вместо добавления недостающих.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, нарушающий сохранение переходов при complete.
    """
    def complete(self):
        """
        Удаляет последний переход, если transitionList не пуст.
        """
        if self.transitionList:
            self.transitionList = self.transitionList[:-1]
        return self
