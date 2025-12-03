"""
Класс FA для работы с конечными автоматами (полуавтоматами)
"""
from __future__ import annotations
from typing import List, Set, Tuple, Any


class FA:
    """Класс для представления конечных автоматов"""

    def __init__(self):
        self.initialState: int | str = 0
        self.finalStates: Set[int | str] = set()
        self.numberOfStates: int = 0
        self.numberOfInputs: int = 0
        self.numberOfOutputs: int = 0
        self.transitionList: List[Tuple] = []
        self.isFSM: int = 0  # 0 - FA, 1 - FSM

    def __str__(self) -> str:
        """Строковое представление автомата"""
        return (f"FA(initial={self.initialState}, "
                f"states={self.numberOfStates}, "
                f"transitions={len(self.transitionList)})")

    def get_states(self) -> Set[int | str]:
        """Получить все состояния автомата"""
        states = set()
        for transition in self.transitionList:
            states.add(transition[0])
            states.add(transition[2])
        return states

    def is_deterministic(self) -> bool:
        """Проверить, является ли автомат детерминированным"""
        state_input_pairs = set()
        for transition in self.transitionList:
            pair = (transition[0], transition[1])
            if pair in state_input_pairs:
                return False
            state_input_pairs.add(pair)
        return True