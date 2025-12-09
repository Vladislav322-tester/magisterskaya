"""
Общие фикстуры для всех тестов FA_simple
"""

import pytest
from src.FA_simple import FA_simple


# ============================================
# ОСНОВНЫЕ ФИКСТУРЫ ДЛЯ СОЗДАНИЯ АВТОМАТОВ
# ============================================

@pytest.fixture
def fa_factory():
    """
    Фабрика для создания объектов FA_simple.

    Пример использования:
    >>> fa = fa_factory(
    >>>     transitions=[(0, "a", 1, "x"), (1, "b", 0, "y")],
    >>>     initial=0,
    >>>     numberOfStates=2,
    >>>     isFSM=1
    >>> )
    """
    def _factory(
        transitions=None,
        initial=None,
        numberOfStates=None,
        numberOfInputs=None,
        finalStates=None,
        isFSM=0,  # По умолчанию FA (0), а не FSM (1)
        numberOfOutputs=None,
    ):
        # Создаем объект
        fa = FA_simple()

        # Устанавливаем переходы (по умолчанию пустой список)
        fa.transitionList = transitions or []

        # Устанавливаем начальное состояние
        if initial is not None:
            fa.initialState = initial
        elif transitions:
            # Берем первое состояние из первого перехода
            fa.initialState = transitions[0][0]
        else:
            fa.initialState = 0

        # Устанавливаем остальные параметры
        if numberOfStates is not None:
            fa.numberOfStates = numberOfStates
        if numberOfInputs is not None:
            fa.numberOfInputs = numberOfInputs
        if finalStates is not None:
            fa.finalStates = finalStates
        if isFSM is not None:
            fa.isFSM = isFSM
        if numberOfOutputs is not None:
            fa.numberOfOutputs = numberOfOutputs

        return fa

    return _factory


# ============================================
# ФИКСТУРЫ ДЛЯ МОКОВ
# ============================================

@pytest.fixture
def mock_efa():
    """Фикстура для MockEFA (для тестирования конвертации)."""
    from tests.mocks.mock_efa import MockEFA
    return MockEFA()


@pytest.fixture
def mock_fa():
    """Фикстура для MockFA (для тестирования конвертации)."""
    from tests.mocks.mock_fa import MockFA
    return MockFA()