"""
Интеграционные тесты преобразований между классами автоматов
"""
import pytest
import sys
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from FA_simple import FA_simple
from tests.mocks.mock_efa import MockEFA
from tests.mocks.mock_fa import MockFA


class TestEFAtoFASimpleIntegration:
    """Интеграционные тесты преобразования EFA -> FA_simple"""

    def test_efa_to_fa_simple_basic_AAA(self):
        """Базовое преобразование EFA в FA_simple"""
        # Arrange
        mock_efa = MockEFA()

        # Act
        fa_simple = FA_simple.from_efa(mock_efa)

        # Assert
        assert isinstance(fa_simple, FA_simple)
        assert fa_simple.initialState == "q0"
        assert len(fa_simple.transitionList) == 2
        # Проверяем, что предикаты и update-функции отброшены
        for transition in fa_simple.transitionList:
            assert len(transition) == 3  # state1, input, state2

    def test_efa_to_fa_simple_state_preservation_AAA(self):
        """Сохранение состояний при преобразовании"""
        # Arrange
        mock_efa = MockEFA()

        # Act
        fa_simple = FA_simple.from_efa(mock_efa)
        states = fa_simple.get_states_list()

        # Assert
        assert "q0" in states
        assert "q1" in states
        assert "q2" in states
        assert len(states) == 3

    def test_efa_to_fa_simple_final_states_AAA(self):
        """Сохранение конечных состояний"""
        # Arrange
        mock_efa = MockEFA()

        # Act
        fa_simple = FA_simple.from_efa(mock_efa)

        # Assert
        assert fa_simple.finalStates == {"q2"}


class TestFAtoFASimpleIntegration:
    """Интеграционные тесты преобразования FA -> FA_simple"""

    def test_fa_to_fa_simple_basic_AAA(self):
        """Базовое преобразование FA в FA_simple"""
        # Arrange
        mock_fa = MockFA()

        # Act
        fa_simple = FA_simple.from_FA(mock_fa)

        # Assert
        assert isinstance(fa_simple, FA_simple)
        assert fa_simple.initialState == "s0"
        assert fa_simple.isFSM == 0
        assert fa_simple.finalStates == {"s2"}

    def test_fa_to_fa_simple_transitions_AAA(self):
        """Сохранение переходов при преобразовании"""
        # Arrange
        mock_fa = MockFA()

        # Act
        fa_simple = FA_simple.from_FA(mock_fa)

        # Assert
        assert len(fa_simple.transitionList) == 4
        # Проверяем формат переходов
        for transition in fa_simple.transitionList:
            assert len(transition) == 3  # FA имеет переходы без выходов


class TestFASimpleChainOperations:
    """Тесты цепочек операций над FA_simple"""

    def test_encode_then_complete_AAA(self, fa_factory):
        """Цепочка: кодирование -> доопределение"""
        # Arrange
        transitions = [("q0", "alpha", "q1", "out1")]
        fa = fa_factory(transitions, numberOfStates=2, numberOfInputs=2)

        # Act
        # 1. Кодируем состояния
        changed1, mapping1, _ = fa.encode_states(forced_transform=True)
        # 2. Кодируем входы/выходы
        result = fa.encode_inputs_outputs(forced_transform=True, dont_change_original=True)

        if isinstance(result, tuple):
            changed2, input_map, output_map = result
            # 3. Доопределяем
            reaction = fa.complete(comptype='loop')
        else:
            new_fa = result
            reaction = new_fa.complete(comptype='loop')

        # Assert
        assert fa.is_complete() or (isinstance(result, FA_simple) and result.is_complete())
        assert isinstance(reaction, int)

    def test_read_write_cycle_AAA(self, tmp_path, fa_factory):
        """Цикл: запись -> чтение -> проверка эквивалентности"""
        # Arrange
        transitions = [(0, "a", 1, "x"), (1, "b", 0, "y")]
        original_fa = fa_factory(transitions, initial=0)
        original_fa.isFSM = 1
        filepath = tmp_path / "cycle_test.fsm"

        # Act
        # 1. Записываем
        original_fa.write_FSM(filepath)
        # 2. Читаем
        loaded_fa = FA_simple.read_FSM(filepath)

        # Assert
        assert isinstance(loaded_fa, FA_simple)
        assert loaded_fa.isFSM == 1
        # Проверяем эквивалентность основных свойств
        assert set(original_fa.get_states_list()) == set(loaded_fa.get_states_list())
        assert set(original_fa.get_actions_list()) == set(loaded_fa.get_actions_list())
        assert len(original_fa.transitionList) == len(loaded_fa.transitionList)


class TestSimulationChain:
    """Тесты цепочек симуляции"""

    def test_move_then_check_AAA(self, fa_factory):
        """Цепочка: симуляция -> проверка принятия"""
        # Arrange
        transitions = [(0, "a", 1), (1, "b", 2)]
        fa = fa_factory(transitions, initial=0, finalStates={2})
        input_seq = ["a", "b"]

        # Act
        # 1. Симулируем
        output_seq, final_state = fa.move_seq_FSM(input_seq)
        # 2. Проверяем принятие
        accepted, fired_trans = fa.accept_FA(input_seq)

        # Assert
        assert final_state == 2
        assert accepted is True
        assert len(fired_trans) == 2

    def test_complete_then_simulate_AAA(self, fa_factory):
        """Цепочка: доопределение -> симуляция"""
        # Arrange
        transitions = [(0, "a", 1, "x")]
        fa = fa_factory(transitions, numberOfStates=2, numberOfInputs=2)
        # Доопределяем
        fa.complete(comptype='loop')

        # Act
        # Симулируем с существующим входом
        output1, state1 = fa.move_seq_FSM(["a"])
        # Симулируем с несуществовавшим ранее входом (должен работать после доопределения)
        output2, state2 = fa.move_seq_FSM(["b"])

        # Assert
        assert output1 is not None
        assert output2 is not None  # Петля должна сработать
        assert state1 == 1
        assert state2 == 0  # Петля возвращает в исходное состояние


if __name__ == "__main__":
    pytest.main([__file__, "-v"])