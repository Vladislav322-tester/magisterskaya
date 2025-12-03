"""
Общие фикстуры для всех тестов
"""
import pytest
import sys
from pathlib import Path
from src.FA_simple import FA_simple

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture
def fa_factory():
    """Фабрика для создания объектов FA_simple"""

    def _factory(transitions, initial=None, numberOfStates=None,
                 numberOfInputs=None, finalStates=None, isFSM=None,
                 numberOfOutputs=None):  # Добавили параметр
        fa = FA_simple()
        fa.transitionList = transitions
        fa.initialState = initial if initial is not None else (
            transitions[0][0] if transitions else None)

        if numberOfStates is not None:
            fa.numberOfStates = numberOfStates
        if numberOfInputs is not None:
            fa.numberOfInputs = numberOfInputs
        if finalStates is not None:
            fa.finalStates = finalStates
        if isFSM is not None:
            fa.isFSM = isFSM
        if numberOfOutputs is not None:  # Добавили обработку
            fa.numberOfOutputs = numberOfOutputs

        return fa

    return _factory


@pytest.fixture
def simple_fa():
    """Простой конечный автомат для тестирования"""
    fa = FA_simple()
    fa.initialState = 0
    fa.numberOfStates = 2
    fa.numberOfInputs = 2
    fa.isFSM = 1
    fa.transitionList = [
        (0, "a", 1, "x"),
        (1, "b", 0, "y")
    ]
    return fa


@pytest.fixture
def sample_transitions():
    """Пример переходов для тестирования"""
    return [
        (0, "a", 1, "x"),
        (1, "b", 0, "y"),
        (0, "b", 2, "z"),
        (2, "a", 1, "w")
    ]


@pytest.fixture
def mock_efa():
    """Фикстура для MockEFA"""
    from tests.mocks.mock_efa import MockEFA
    return MockEFA()


@pytest.fixture
def mock_fa():
    """Фикстура для MockFA"""
    from tests.mocks.mock_fa import MockFA
    return MockFA()