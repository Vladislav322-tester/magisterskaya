"""
MUT-01: грубая логическая мутация.

Метод __eq__ всегда возвращает False. Это контрольный мутант,
который должен легко обнаруживаться тестами.
"""

from src.FA_simple import FA_simple as FA_simple_orig


class FA_simple(FA_simple_orig):

    """
    Мутант legacy FA_simple, намеренно искажающий сравнение автоматов.
    """
    def __eq__(self, other):
        """
        Возвращает False для любого сравнения.
        """
        return False
