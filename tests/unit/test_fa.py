"""
Модульные тесты для класса FA
"""
import pytest
import sys
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

try:
    from FA import FA

    FA_AVAILABLE = True
except ImportError:
    FA_AVAILABLE = False
    FA = None


@pytest.mark.skipif(not FA_AVAILABLE, reason="Класс FA не найден")
class TestFAInitialization:
    """Тесты инициализации класса FA"""

    def test_init_AAA(self):
        """Тест конструктора класса FA"""
        # Arrange & Act
        fa = FA()
        # Assert
        assert fa.initialState == 0
        assert fa.numberOfStates == 0
        assert len(fa.transitionList) == 0
        assert fa.isFSM == 0
        assert fa.finalStates == set()

    def test_str_representation_AAA(self):
        """Тест строкового представления"""
        # Arrange
        fa = FA()
        fa.initialState = "q0"
        fa.numberOfStates = 3
        fa.transitionList = [("q0", "a", "q1"), ("q1", "b", "q2")]
        # Act
        result = str(fa)
        # Assert
        assert "FA" in result
        assert "q0" in result
        assert "3" in result


@pytest.mark.skipif(not FA_AVAILABLE, reason="Класс FA не найден")
class TestFAMethods:
    """Тесты методов класса FA"""

    def test_get_states_AAA(self):
        """Тест получения всех состояний"""
        # Arrange
        fa = FA()
        fa.transitionList = [
            ("q0", "a", "q1"),
            ("q1", "b", "q2"),
            ("q2", "c", "q0")
        ]
        # Act
        states = fa.get_states()
        # Assert
        assert states == {"q0", "q1", "q2"}

    def test_is_deterministic_true_AAA(self):
        """Тест детерминированности для детерминированного FA"""
        # Arrange
        fa = FA()
        fa.transitionList = [
            ("q0", "a", "q1"),
            ("q1", "b", "q2"),
            ("q2", "c", "q0"),
            ("q0", "d", "q2")
        ]
        # Act
        result = fa.is_deterministic()
        # Assert
        assert result is True

    def test_is_deterministic_false_AAA(self):
        """Тест детерминированности для недетерминированного FA"""
        # Arrange
        fa = FA()
        fa.transitionList = [
            ("q0", "a", "q1"),
            ("q0", "a", "q2"),  # Два перехода из q0 по 'a'
            ("q1", "b", "q2")
        ]
        # Act
        result = fa.is_deterministic()
        # Assert
        assert result is False

    def test_set_final_states_AAA(self):
        """Тест установки конечных состояний"""
        # Arrange
        fa = FA()
        # Act
        fa.finalStates = {1, 2, 3}
        # Assert
        assert fa.finalStates == {1, 2, 3}
        assert len(fa.finalStates) == 3


@pytest.mark.skipif(not FA_AVAILABLE, reason="Класс FA не найден")
class TestFATransitions:
    """Тесты работы с переходами"""

    def test_add_transition_AAA(self):
        """Тест добавления переходов"""
        # Arrange
        fa = FA()
        # Act
        fa.transitionList.append(("s0", "a", "s1"))
        fa.transitionList.append(("s1", "b", "s2"))
        # Assert
        assert len(fa.transitionList) == 2
        assert fa.transitionList[0] == ("s0", "a", "s1")

    def test_transition_format_AAA(self):
        """Тест формата переходов"""
        # Arrange
        fa = FA()
        transitions = [
            (0, "input1", 1),
            ("stateA", "input2", "stateB"),
            (2, 3, 4)  # Числовые входы
        ]
        # Act
        fa.transitionList = transitions
        # Assert
        assert len(fa.transitionList) == 3
        assert fa.transitionList[1] == ("stateA", "input2", "stateB")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])