"""
Моки для класса FA
"""
from typing import List, Tuple, Set, Any


class MockFA:
    """Заглушка для класса FA"""

    def __init__(self):
        self.transitionList: List[Tuple] = [
            ("s0", "a", "s1"),
            ("s1", "b", "s2"),
            ("s2", "c", "s0"),
            ("s0", "d", "s2")
        ]
        self.initialState: str = "s0"
        self.isFSM: int = 0
        self.finalStates: Set[str] = {"s2"}
        self.numberOfStates: int = 3
        self.numberOfInputs: int = 4
        self.numberOfOutputs: int = 0

    def __str__(self) -> str:
        return f"MockFA(states={self.numberOfStates}, transitions={len(self.transitionList)})"

    def get_states(self) -> Set[str]:
        """Получить все состояния"""
        states = set()
        for trans in self.transitionList:
            states.add(trans[0])
            states.add(trans[2])
        return states

    def is_deterministic(self) -> bool:
        """Проверить детерминированность"""
        seen = set()
        for trans in self.transitionList:
            key = (trans[0], trans[1])
            if key in seen:
                return False
            seen.add(key)
        return True


class MockFADeterministic(MockFA):
    """Детерминированный FA"""

    def __init__(self):
        super().__init__()
        # Переопределяем переходы для детерминированности
        self.transitionList = [
            (0, "a", 1),
            (1, "b", 2),
            (2, "a", 0),
            (0, "c", 2),
            (1, "c", 0),
            (2, "b", 1)
        ]
        self.initialState = 0
        self.finalStates = {2}
        self.numberOfStates = 3
        self.numberOfInputs = 3


class MockFANonDeterministic(MockFA):
    """Недетерминированный FA"""

    def __init__(self):
        super().__init__()
        # Создаем недетерминированные переходы
        self.transitionList = [
            (0, "a", 1),
            (0, "a", 2),  # Недетерминированный переход
            (1, "b", 2),
            (2, "a", 0),
            (1, "a", 0)
        ]
        self.initialState = 0
        self.finalStates = {2}
        self.numberOfStates = 3
        self.numberOfInputs = 2