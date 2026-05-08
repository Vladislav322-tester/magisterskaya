"""
MUT-10
Completeness мутация.

complete() удаляет переходы вместо добавления.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    def complete(self):
        if self.transitionList:
            self.transitionList = self.transitionList[:-1]
        return self
