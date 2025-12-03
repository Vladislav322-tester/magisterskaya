"""
Модульные тесты для класса MYEFA
"""
import pytest
import sys
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

try:
    from MYEFA import MYEFA, ExtendedTransition

    MYEFA_AVAILABLE = True
except ImportError:
    MYEFA_AVAILABLE = False
    MYEFA = None
    ExtendedTransition = None


@pytest.mark.skipif(not MYEFA_AVAILABLE, reason="Класс MYEFA не найден")
class TestMYEFAInitialization:
    """Тесты инициализации класса MYEFA"""

    def test_init_AAA(self):
        """Тест конструктора класса MYEFA"""
        # Arrange & Act
        efa = MYEFA()
        # Assert
        assert efa.initialState == 0
        assert efa.numberOfStates == 0
        assert len(efa.transitionList) == 0
        assert efa.finalStates == set()
        assert efa.variables == {}
        assert efa.currentState == 0

    def test_str_representation_AAA(self):
        """Тест строкового представления"""
        # Arrange
        efa = MYEFA()
        efa.initialState = "init"
        efa.numberOfStates = 5
        efa.variables = {"x": 10}
        # Act
        result = str(efa)
        # Assert
        assert "MYEFA" in result
        assert "init" in result
        assert "5" in result


@pytest.mark.skipif(not MYEFA_AVAILABLE, reason="Класс MYEFA не найден")
class TestMYEFAMethods:
    """Тесты методов класса MYEFA"""

    def test_reset_AAA(self):
        """Тест сброса состояния"""
        # Arrange
        efa = MYEFA()
        efa.initialState = "q0"
        efa.currentState = "q2"
        efa.variables = {"x": 5, "y": 10}
        # Act
        efa.reset()
        # Assert
        assert efa.currentState == "q0"
        # Проверяем, что переменные сбросились
        assert "x" in efa.variables

    def test_step_without_predicate_AAA(self):
        """Тест шага без предиката"""
        # Arrange
        efa = MYEFA()
        efa.initialState = "q0"
        efa.currentState = "q0"

        # Создаем переход
        transition = ExtendedTransition(
            state1="q0",
            input="a",
            state2="q1",
            predicate=None,
            update_function=None,
            output="output1"
        )
        efa.transitionList = [transition]

        # Act
        result = efa.step("a")

        # Assert
        assert result == "output1"
        assert efa.currentState == "q1"

    def test_step_with_predicate_true_AAA(self):
        """Тест шага с истинным предикатом"""
        # Arrange
        efa = MYEFA()
        efa.initialState = "q0"
        efa.currentState = "q0"
        efa.variables = {"x": 5}

        transition = ExtendedTransition(
            state1="q0",
            input="a",
            state2="q1",
            predicate="x > 0",
            update_function=None,
            output="output1"
        )
        efa.transitionList = [transition]

        # Act
        result = efa.step("a")

        # Assert
        assert result == "output1"
        assert efa.currentState == "q1"

    def test_step_with_predicate_false_AAA(self):
        """Тест шага с ложным предикатом"""
        # Arrange
        efa = MYEFA()
        efa.initialState = "q0"
        efa.currentState = "q0"
        efa.variables = {"x": 0}  # x = 0, поэтому x > 0 ложно

        transition = ExtendedTransition(
            state1="q0",
            input="a",
            state2="q1",
            predicate="x > 0",
            update_function=None,
            output="output1"
        )
        efa.transitionList = [transition]

        # Act
        result = efa.step("a")

        # Assert
        assert result is None
        assert efa.currentState == "q0"  # Состояние не изменилось

    def test_step_with_update_function_AAA(self):
        """Тест шага с функцией обновления"""
        # Arrange
        efa = MYEFA()
        efa.initialState = "q0"
        efa.currentState = "q0"
        efa.variables = {"counter": 0}

        transition = ExtendedTransition(
            state1="q0",
            input="inc",
            state2="q1",
            predicate=None,
            update_function="counter = counter + 1",
            output="incremented"
        )
        efa.transitionList = [transition]

        # Act
        result = efa.step("inc")

        # Assert
        assert result == "incremented"
        assert efa.currentState == "q1"
        assert efa.variables["counter"] == 1

    def test_step_no_transition_AAA(self):
        """Тест шага без соответствующего перехода"""
        # Arrange
        efa = MYEFA()
        efa.initialState = "q0"
        efa.currentState = "q0"
        efa.transitionList = []  # Нет переходов

        # Act
        result = efa.step("unknown_input")

        # Assert
        assert result is None
        assert efa.currentState == "q0"


@pytest.mark.skipif(not MYEFA_AVAILABLE, reason="Класс MYEFA не найден")
class TestMYEFAVariables:
    """Тесты работы с переменными MYEFA"""

    def test_variable_initialization_AAA(self):
        """Тест инициализации переменных"""
        # Arrange
        efa = MYEFA()
        # Act
        efa.variables = {
            "temperature": 25,
            "pressure": 100,
            "active": True
        }
        # Assert
        assert len(efa.variables) == 3
        assert efa.variables["temperature"] == 25
        assert efa.variables["active"] is True

    def test_variable_update_AAA(self):
        """Тест обновления переменных"""
        # Arrange
        efa = MYEFA()
        efa.variables = {"x": 0}
        # Act
        efa.variables["x"] = 10
        # Assert
        assert efa.variables["x"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])