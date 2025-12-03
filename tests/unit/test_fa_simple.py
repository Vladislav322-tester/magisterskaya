"""
Модульные тесты для класса FA_simple
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from FA_simple import FA_simple
from tests.mocks.mock_efa import MockEFA
from tests.mocks.mock_fa import MockFA
from data_samples import SAMPLES

parametrize_sample = pytest.mark.parametrize(
    "transitions, final_state, input_seq, expected_accept",
    SAMPLES[:5]  # Берем первые 5 примеров для скорости
)


class TestFASimpleInitialization:
    """Тесты инициализации и базовых операций"""

    def test_init_AAA(self):
        """Тест конструктора класса FA_simple"""
        # Arrange
        automaton = FA_simple()
        # Act — нет действий
        # Assert
        assert automaton.initialState == 0
        assert automaton.numberOfStates == 0
        assert automaton.transitionList == []

    def test_equality_AAA(self, fa_factory):
        """Тест оператора равенства автоматов"""
        # Arrange
        transitions = [("s1", "a", "s2", "x"), ("s2", "b", "s3", "y")]
        automaton1 = fa_factory(transitions)
        automaton2 = fa_factory(transitions)
        # Act & Assert
        assert automaton1 == automaton2

    def test_inequality_AAA(self, fa_factory):
        """Тест неравенства автоматов"""
        # Arrange
        transitions1 = [("s1", "a", "s2", "x")]
        transitions2 = [("s1", "b", "s2", "y")]
        automaton1 = fa_factory(transitions1)
        automaton2 = fa_factory(transitions2)
        # Act & Assert
        assert automaton1 != automaton2


class TestFASimpleIOOperations:
    """Тесты операций ввода/вывода"""

    def test_write_fsm_AAA(self, tmp_path, fa_factory):
        """Тест записи FSM в файл"""
        # Arrange
        transitions = [("s0", "a", "s1", "x"), ("s1", "b", "s0", "y")]
        fa = fa_factory(transitions, initial="s0")
        filepath = tmp_path / "test.fsm"
        # Act
        fa.write_FSM(filepath)
        # Assert
        assert filepath.exists()
        assert filepath.stat().st_size > 0

    def test_read_fsm_AAA(self, tmp_path, fa_factory):
        """Тест чтения FSM из файла"""
        # Arrange
        transitions = [(0, "a", 1, "x"), (1, "b", 0, "y")]
        fa = fa_factory(transitions, initial=0)
        fa.isFSM = 1
        filepath = tmp_path / "test_read.fsm"
        fa.write_FSM(filepath)

        # Act
        loaded_fa = FA_simple.read_FSM(filepath)

        # Assert
        assert isinstance(loaded_fa, FA_simple)
        assert loaded_fa.isFSM == 1
        assert len(loaded_fa.transitionList) == 2

    def test_read_fa_AAA(self):
        """Тест чтения FA из файла"""
        # Arrange
        fa_content = """states_number 3
actions_number 2
start_state 0
final_state 2
0 a 1
1 b 2
0 b 2"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.fa', delete=False) as f:
            f.write(fa_content)
            temp_file = f.name

        try:
            # Act
            fa = FA_simple.read_FA(temp_file)
            # Assert
            assert isinstance(fa, FA_simple)
            assert fa.initialState == 0
            assert fa.finalStates == {2}
            assert len(fa.transitionList) == 3
        finally:
            os.unlink(temp_file)


class TestFASimpleStaticMethods:
    """Тесты статических методов преобразования"""

    def test_from_efa_AAA(self):
        """Тест преобразования из EFA в FA_simple"""
        # Arrange
        mock_efa = MockEFA()
        # Act
        result = FA_simple.from_efa(mock_efa)
        # Assert
        assert isinstance(result, FA_simple)
        assert result.initialState == "q0"
        assert len(result.transitionList) == 2

    def test_from_fa_AAA(self):
        """Тест преобразования из FA в FA_simple"""
        # Arrange
        mock_fa = MockFA()
        # Act
        result = FA_simple.from_FA(mock_fa)
        # Assert
        assert isinstance(result, FA_simple)
        assert result.initialState == "s0"
        assert result.isFSM == 0


class TestFASimpleGetters:
    """Тесты getter-методов"""

    def test_get_states_list_AAA(self, fa_factory):
        """Тест получения списка состояний"""
        # Arrange
        transitions = [(0, "a", 1, "x"), (1, "b", 2, "y"), (2, "c", 0, "z")]
        fa = fa_factory(transitions)
        # Act
        states = fa.get_states_list()
        # Assert
        assert set(states) == {0, 1, 2}
        assert len(states) == 3

    def test_get_actions_list_AAA(self, fa_factory):
        """Тест получения списка действий"""
        # Arrange
        transitions = [(0, "a", 1, "x"), (1, "b", 2, "y"), (0, "c", 2, "z")]
        fa = fa_factory(transitions)
        # Act
        actions = fa.get_actions_list()
        # Assert
        assert set(actions) == {"a", "b", "c"}

    def test_get_outputs_list_AAA(self, fa_factory):
        """Тест получения списка выходов"""
        # Arrange
        transitions = [(0, "a", 1, "x"), (1, "b", 2, "y"), (2, "c", 0, "z")]
        fa = fa_factory(transitions)
        fa.isFSM = 1
        # Act
        outputs = fa.get_outputs_list()
        # Assert
        assert set(outputs) == {"x", "y", "z"}

    def test_get_ns_out_AAA(self, fa_factory):
        """Тест получения следующего состояния и реакции"""
        # Arrange
        transitions = [(0, "a", 1, "x"), (1, "b", 2, "y")]
        fa = fa_factory(transitions)
        fa.isFSM = 1
        # Act
        next_state, reaction = fa.get_ns_out(0, "a")
        # Assert
        assert next_state == 1
        assert reaction == "x"

    def test_get_ns_out_error_AAA(self, fa_factory):
        """Тест ошибки при получении несуществующего перехода"""
        # Arrange
        transitions = [(0, "a", 1, "x")]
        fa = fa_factory(transitions)
        # Act & Assert
        with pytest.raises(Exception, match="get_ns_out error"):
            fa.get_ns_out(0, "b")


class TestFASimpleChecks:
    """Тесты методов проверки"""

    def test_is_complete_complete_AAA(self, fa_factory):
        """Тест проверки полноты для полного автомата"""
        # Arrange
        transitions = [
            (0, "a", 0, "x"), (0, "b", 1, "y"),
            (1, "a", 1, "z"), (1, "b", 0, "w")
        ]
        fa = fa_factory(transitions, numberOfStates=2, numberOfInputs=2)
        # Act
        result = fa.is_complete()
        # Assert
        assert result is True

    def test_is_complete_incomplete_AAA(self, fa_factory):
        """Тест проверки полноты для неполного автомата"""
        # Arrange
        transitions = [(0, "a", 1, "x")]
        fa = fa_factory(transitions, numberOfStates=2, numberOfInputs=2)
        # Act
        result = fa.is_complete()
        # Assert
        assert result is False

    def test_check_states_consistency_AAA(self, fa_factory):
        """Тест согласованности типов состояний"""
        # Arrange
        transitions = [(0, "a", 1, "x"), (1, "b", 2, "y")]
        fa = fa_factory(transitions)
        # Act
        result = fa.check_states_for_consistency()
        # Assert
        assert result is True

    def test_check_inputs_outputs_consistency_AAA(self, fa_factory):
        """Тест согласованности типов входов/выходов"""
        # Arrange
        transitions = [(0, "a", 1, "x"), (1, "b", 2, "y")]
        fa = fa_factory(transitions)
        # Act
        result = fa.check_inputs_outputs_for_consistency()
        # Assert
        assert result is True


class TestFASimpleTransformations:
    """Тесты методов преобразования автоматов"""

    def test_rename_inputs_AAA(self, fa_factory):
        """Тест переименования входов"""
        # Arrange
        transitions = [(0, "a", 1, "x"), (1, "b", 0, "y")]
        fa = fa_factory(transitions)
        rename_map = {"a": "input1", "b": "input2"}
        # Act
        fa.rename_inputs(rename_map)
        # Assert
        inputs = {tr[1] for tr in fa.transitionList}
        assert inputs == {"input1", "input2"}

    def test_sort_trans_table_AAA(self, fa_factory):
        """Тест сортировки таблицы переходов"""
        # Arrange
        transitions = [(2, "z", 3, "c"), (0, "a", 1, "x"), (1, "b", 2, "y")]
        fa = fa_factory(transitions)
        unsorted = fa.transitionList.copy()
        # Act
        fa.sort_trans_table()
        # Assert
        assert fa.transitionList != unsorted
        # Проверяем сортировку по состоянию и входу
        for i in range(len(fa.transitionList) - 1):
            curr = fa.transitionList[i]
            next_ = fa.transitionList[i + 1]
            assert (curr[0], curr[1]) <= (next_[0], next_[1])

    def test_encode_states_AAA(self, fa_factory):
        """Тест кодирования состояний"""
        # Arrange
        transitions = [("q0", "a", "q1", "x"), ("q1", "b", "q2", "y")]
        fa = fa_factory(transitions)
        # Act
        changed, mapping, _ = fa.encode_states(forced_transform=True)
        # Assert
        assert changed is True
        assert isinstance(mapping, dict)
        # Проверяем, что состояния стали числами
        for tr in fa.transitionList:
            assert isinstance(tr[0], int)
            assert isinstance(tr[2], int)

    def test_encode_inputs_outputs_AAA(self, fa_factory):
        """Тест кодирования входов и выходов"""
        # Arrange
        transitions = [("q0", "alpha", "q1", "out1"), ("q1", "beta", "q2", "out2")]
        fa = fa_factory(transitions)
        # Act
        result = fa.encode_inputs_outputs(forced_transform=True, dont_change_original=True)
        # Assert
        if isinstance(result, tuple):
            changed, input_map, output_map = result
            assert isinstance(input_map, dict)
            assert isinstance(output_map, dict)
        else:
            # Если вернулся новый автомат
            new_fa = result
            assert isinstance(new_fa, FA_simple)
            for tr in new_fa.transitionList:
                assert isinstance(tr[1], int)
                assert isinstance(tr[3], int)

    def test_complete_loop_AAA(self, fa_factory):
        """Тест доопределения автомата петлями"""
        # Arrange
        transitions = [(0, "a", 1, "x")]
        fa = fa_factory(transitions, numberOfStates=2, numberOfInputs=2)
        assert not fa.is_complete()
        # Act
        reaction = fa.complete(comptype='loop')
        # Assert
        assert fa.is_complete()
        assert isinstance(reaction, int)
        # Проверяем добавленные петли
        loop_transitions = [tr for tr in fa.transitionList
                            if tr[0] == tr[2] and tr[3] == reaction]
        assert len(loop_transitions) > 0

    def test_complete_dcs_AAA(self, fa_factory):
        """Тест доопределения с помощью DCS"""
        # Arrange
        transitions = [(0, "a", 1, "x")]
        fa = fa_factory(transitions, numberOfStates=2, numberOfInputs=2)
        original_states = fa.numberOfStates
        # Act
        reaction = fa.complete(comptype='DCS', reaction=999)
        # Assert
        assert fa.is_complete()
        assert fa.numberOfStates == original_states + 1
        assert reaction == 999


class TestFASimpleSimulation:
    """Тесты методов симуляции"""

    def test_move_seq_fsm_AAA(self, fa_factory):
        """Тест симуляции FSM"""
        # Arrange
        transitions = [(0, "a", 1, "x"), (1, "b", 2, "y"), (2, "c", 0, "z")]
        fa = fa_factory(transitions, initial=0)
        fa.isFSM = 1
        input_seq = ["a", "b", "c"]
        # Act
        output_seq, final_state = fa.move_seq_FSM(input_seq)
        # Assert
        assert output_seq == ["x", "y", "z"]
        assert final_state == 0

    def test_move_seq_fsm_invalid_AAA(self, fa_factory):
        """Тест симуляции с неверной входной последовательностью"""
        # Arrange
        transitions = [(0, "a", 1, "x")]
        fa = fa_factory(transitions, initial=0)
        input_seq = ["b"]  # Несуществующий вход
        # Act
        output_seq, final_state = fa.move_seq_FSM(input_seq)
        # Assert
        assert output_seq is None
        assert final_state is None

    def test_accept_fa_AAA(self, fa_factory):
        """Тест принятия последовательности FA"""
        # Arrange
        transitions = [(0, "a", 1), (1, "b", 2)]
        fa = fa_factory(transitions, initial=0, finalStates={2})
        fa.isFSM = 0
        input_seq = ["a", "b"]
        # Act
        accepted, fired_trans = fa.accept_FA(input_seq)
        # Assert
        assert accepted is True
        assert isinstance(fired_trans, set)
        assert len(fired_trans) == 2

    def test_reject_fa_AAA(self, fa_factory):
        """Тест отклонения последовательности FA"""
        # Arrange
        transitions = [(0, "a", 1), (1, "b", 2)]
        fa = fa_factory(transitions, initial=0, finalStates={1})
        input_seq = ["a", "b"]
        # Act
        accepted, fired_trans = fa.accept_FA(input_seq)
        # Assert
        assert accepted is False
        assert len(fired_trans) == 2


# Параметризованные тесты
@parametrize_sample
def test_param_get_states_AAA(fa_factory, transitions, final_state,
                              input_seq, expected_accept):
    """Параметризованный тест получения состояний"""
    # Arrange
    fa = fa_factory(transitions)
    # Act
    states = fa.get_states_list()
    # Assert
    expected_states = {tr[0] for tr in transitions} | {tr[2] for tr in transitions}
    assert set(states) == expected_states


@parametrize_sample
def test_param_get_actions_AAA(fa_factory, transitions, final_state,
                               input_seq, expected_accept):
    """Параметризованный тест получения действий"""
    # Arrange
    fa = fa_factory(transitions)
    # Act
    actions = fa.get_actions_list()
    # Assert
    expected_actions = {tr[1] for tr in transitions}
    assert set(actions) == expected_actions


@parametrize_sample
def test_param_is_complete_AAA(fa_factory, transitions, final_state,
                               input_seq, expected_accept):
    """Параметризованный тест проверки полноты"""
    # Arrange
    fa = fa_factory(transitions, numberOfStates=4, numberOfInputs=2)
    # Act
    result = fa.is_complete()
    # Assert
    assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])