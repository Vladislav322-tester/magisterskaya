"""
Общие фикстуры для всех тестов с поддержкой Hypothesis
"""

import sys
from pathlib import Path

import pytest
from hypothesis import strategies as st, given, settings, assume

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.FA_simple import FA_simple

# Импортируем наши стратегии
try:
    from tests.hypothesis_strategies.base_strategies import (
        state_strategy,
        simple_input,
        output_strategy,
        valid_transition,
        can_convert_to_int
    )
    from tests.hypothesis_strategies.smart_strategies import (
        automaton_data,
        deterministic_automaton,
        complete_automaton,
        input_sequence_for_automaton,
        create_fa_from_data
    )
    HAS_HYPOTHESIS_STRATEGIES = True
except ImportError:
    HAS_HYPOTHESIS_STRATEGIES = False


@pytest.fixture
def fa_factory():
    """Фабрика для создания объектов FA_simple с поддержкой Hypothesis"""

    def _factory(
        transitions,
        initial=None,
        numberOfStates=None,
        numberOfInputs=None,
        finalStates=None,
        isFSM=None,
        numberOfOutputs=None,
    ):
        # Arrange
        fa = FA_simple()
        fa.transitionList = transitions

        # Устанавливаем начальное состояние
        if initial is not None:
            fa.initialState = initial
        elif transitions:
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


@pytest.fixture
def simple_fa(fa_factory):
    """Простой конечный автомат для тестирования (с использованием фабрики)"""
    # Arrange
    return fa_factory(
        transitions=[(0, "a", 1, "x"), (1, "b", 0, "y")],
        initial=0,
        numberOfStates=2,
        numberOfInputs=2,
        isFSM=1,
        numberOfOutputs=2
    )


@pytest.fixture
def sample_transitions():
    """Пример переходов для тестирования"""
    return [(0, "a", 1, "x"), (1, "b", 0, "y"), (0, "b", 2, "z"), (2, "a", 1, "w")]


# Hypothesis-фикстуры (только если стратегии доступны)
if HAS_HYPOTHESIS_STRATEGIES:

    @pytest.fixture
    def random_fsm():
        """Случайный FSM, сгенерированный Hypothesis"""
        @given(data=automaton_data(min_states=1, max_states=3, is_fsm=True))
        @settings(max_examples=1, deadline=None)
        def create_random_fsm(data):
            return create_fa_from_data(data)

        # Немного хак, но работает для фикстур
        class RandomFSMFactory:
            def get(self):
                result = []
                create_random_fsm(lambda d: result.append(d))
                return result[0] if result else None

        factory = RandomFSMFactory()
        return factory.get()

    @pytest.fixture
    def random_fa():
        """Случайный FA, сгенерированный Hypothesis"""
        @given(data=automaton_data(min_states=1, max_states=3, is_fsm=False))
        @settings(max_examples=1, deadline=None)
        def create_random_fa(data):
            return create_fa_from_data(data)

        class RandomFAFactory:
            def get(self):
                result = []
                create_random_fa(lambda d: result.append(d))
                return result[0] if result else None

        factory = RandomFAFactory()
        return factory.get()

    @pytest.fixture
    def deterministic_fsm():
        """Детерминированный FSM, сгенерированный Hypothesis"""
        @given(data=deterministic_automaton(is_fsm=True))
        @settings(max_examples=1, deadline=None)
        def create_deterministic_fsm(data):
            return create_fa_from_data(data)

        class DeterministicFSMFactory:
            def get(self):
                result = []
                create_deterministic_fsm(lambda d: result.append(d))
                return result[0] if result else None

        factory = DeterministicFSMFactory()
        return factory.get()


# Фикстуры для моков (оставляем как есть)
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


# Декораторы для удобства
def hypothesis_test(**kwargs):
    """Декоратор для Hypothesis тестов с настройками по умолчанию"""
    default_settings = {
        'max_examples': 10,
        'deadline': None,
        'suppress_health_check': ['too_slow', 'large_base_example']
    }
    default_settings.update(kwargs)

    def decorator(test_func):
        return settings(**default_settings)(given()(test_func))

    return decorator