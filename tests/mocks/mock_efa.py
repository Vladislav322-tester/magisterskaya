"""
Моки для класса MYEFA
"""

from collections import namedtuple
from typing import Any, Dict, List, Set


class MockEFA:
    """Заглушка для класса MYEFA с реализацией основных методов"""

    def __init__(self):
        self.Transition = namedtuple(
            "Transition",
            ["state1", "input", "state2", "predicate", "update_function", "output"],
        )

        self.transitionList: List[Any] = [
            self.Transition("q0", "a", "q1", None, None, "output1"),
            self.Transition("q1", "b", "q2", "x > 0", "x = x + 1", "output2"),
        ]
        self.initialState: str = "q0"
        self.finalStates: Set[str] = {"q2"}
        self.numberOfStates: int = 3
        self.variables: Dict[str, Any] = {"x": 0}
        self.currentState: str = "q0"

    def reset(self) -> None:
        """Сбросить состояние автомата"""
        self.currentState = self.initialState
        self.variables["x"] = 0

    def step(self, input_symbol: str, **kwargs) -> Any:
        """
        Выполнить один шаг автомата

        Args:
            input_symbol: Входной символ
            **kwargs: Дополнительные параметры

        Returns:
            Выходной символ или None
        """
        for transition in self.transitionList:
            if (
                transition.state1 == self.currentState
                and transition.input == input_symbol
            ):

                # Проверяем предикат
                if transition.predicate:
                    if not self._check_predicate(transition.predicate, kwargs):
                        continue

                # Обновляем состояние
                self.currentState = transition.state2

                # Выполняем update функцию
                if transition.update_function:
                    self._execute_update(transition.update_function)

                return transition.output

        return None

    def _check_predicate(self, predicate: str, context: Dict) -> bool:
        """Проверить предикат"""
        # Упрощенная реализация для тестов
        if predicate == "x > 0":
            return self.variables.get("x", 0) > 0
        return True

    def _execute_update(self, update_func: str) -> None:
        """Выполнить функцию обновления"""
        if update_func == "x = x + 1":
            self.variables["x"] = self.variables.get("x", 0) + 1


class MockEFAComplex(MockEFA):
    """Более сложная заглушка MYEFA с дополнительной логикой"""

    def __init__(self):
        super().__init__()
        # Добавляем больше переходов
        self.transitionList.extend(
            [
                self.Transition("q2", "c", "q0", None, None, "output3"),
                self.Transition("q0", "d", "q2", "x < 10", "x = x * 2", "output4"),
            ]
        )
        self.numberOfStates = 4
        self.variables = {"x": 0, "y": 5, "active": True}

    def _check_predicate(self, predicate: str, context: Dict) -> bool:
        """Расширенная проверка предикатов"""
        if predicate == "x < 10":
            return self.variables.get("x", 0) < 10
        elif predicate == "active == True":
            return self.variables.get("active", False) is True
        return super()._check_predicate(predicate, context)
