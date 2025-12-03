"""
Класс MYEFA для работы с расширенными конечными автоматами
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from collections import namedtuple

# Определение структуры перехода для расширенного автомата
ExtendedTransition = namedtuple(
    'ExtendedTransition',
    ['state1', 'input', 'state2', 'predicate', 'update_function', 'output']
)


class MYEFA:
    """Класс для представления расширенных конечных автоматов"""

    def __init__(self):
        self.initialState: int | str = 0
        self.finalStates: Set[int | str] = set()
        self.numberOfStates: int = 0
        self.variables: Dict[str, Any] = {}
        self.transitionList: List[ExtendedTransition] = []
        self.currentState: int | str = 0

    def __str__(self) -> str:
        """Строковое представление расширенного автомата"""
        return (f"MYEFA(initial={self.initialState}, "
                f"states={self.numberOfStates}, "
                f"variables={len(self.variables)}, "
                f"transitions={len(self.transitionList)})")

    def reset(self) -> None:
        """Сбросить автомат в начальное состояние"""
        self.currentState = self.initialState
        # Сброс переменных к начальным значениям
        for var_name, initial_value in self.variables.items():
            if isinstance(initial_value, tuple) and len(initial_value) == 2:
                self.variables[var_name] = initial_value[0]

    def step(self, input_symbol: Any, **kwargs) -> Optional[Any]:
        """
        Выполнить один шаг автомата

        Args:
            input_symbol: Входной символ
            **kwargs: Значения переменных для проверки предикатов

        Returns:
            Выходной символ или None, если переход невозможен
        """
        for transition in self.transitionList:
            if (transition.state1 == self.currentState and
                    transition.input == input_symbol):
                # Проверка предиката (если есть)
                if transition.predicate:
                    predicate_result = self._evaluate_predicate(
                        transition.predicate, kwargs)
                    if not predicate_result:
                        continue

                # Обновление состояния
                self.currentState = transition.state2

                # Выполнение update функции (если есть)
                if transition.update_function:
                    self._execute_update_function(
                        transition.update_function, kwargs)

                return transition.output

        return None

    def _evaluate_predicate(self, predicate: str, context: Dict) -> bool:
        """Вычислить значение предиката"""
        # Простая реализация - в реальном проекте нужно парсить выражение
        try:
            # Безопасное вычисление с ограниченным контекстом
            safe_locals = {**self.variables, **context}
            return bool(eval(predicate, {"__builtins__": {}}, safe_locals))
        except:
            return False

    def _execute_update_function(self, update_func: str, context: Dict) -> None:
        """Выполнить функцию обновления переменных"""
        try:
            safe_locals = {**self.variables, **context}
            exec(update_func, {"__builtins__": {}}, safe_locals)
            # Обновляем переменные, которые могли измениться
            for var_name in self.variables:
                if var_name in safe_locals:
                    self.variables[var_name] = safe_locals[var_name]
        except:
            pass