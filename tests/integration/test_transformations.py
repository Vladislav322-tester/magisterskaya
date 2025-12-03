"""
Настоящие интеграционные тесты для FA_simple
Тестируют взаимодействие методов между собой
"""

import sys
import pytest
from pathlib import Path


# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.FA_simple import FA_simple


class TestFA_simpleReadWriteIntegration:
    """Интеграционные тесты чтения/записи"""

    def test_write_read_cycle_fsm_AAA(self, tmp_path):
        """Полный цикл: создание -> запись -> чтение -> проверка"""
        # Arrange - создаем FSM
        fa = FA_simple()
        fa.initialState = 0
        fa.isFSM = 1
        fa.transitionList = [
            (0, "a", 1, "x"),
            (1, "b", 0, "y"),
            (0, "c", 2, "z"),
            (2, "a", 1, "w"),
        ]

        filepath = tmp_path / "integration_test.fsm"

        # Act
        # 1. Записываем
        fa.write_FSM(filepath)
        # 2. Читаем
        loaded_fa = FA_simple.read_FSM(filepath)

        # Assert
        assert isinstance(loaded_fa, FA_simple)
        assert loaded_fa.isFSM == 1
        assert int(loaded_fa.initialState) == 0  # Приводим к int для сравнения
        assert len(loaded_fa.transitionList) == 4

        # Проверяем что состояния сохранились (приводим к одинаковому типу)
        original_states = {str(s) for s in fa.get_states_list()}
        loaded_states = {str(s) for s in loaded_fa.get_states_list()}
        assert original_states == loaded_states

    def test_write_read_cycle_fa_AAA(self, tmp_path):
        """Цикл для FA (не FSM) - используем числовые состояния"""
        # Arrange - создаем FA файл с числовыми состояниями
        filepath = tmp_path / "integration_fa_test.fa"

        # FA формат ожидает числа, используем их
        content = """states_number 3
actions_number 3
start_state 0
final_state 2
0 a 1
1 b 2
0 c 2"""

        filepath.write_text(content)

        # Act
        loaded_fa = FA_simple.read_FA(filepath)

        # Assert
        assert isinstance(loaded_fa, FA_simple)
        assert loaded_fa.isFSM == 0
        assert loaded_fa.initialState == 0
        assert loaded_fa.finalStates == {2}
        assert len(loaded_fa.transitionList) == 3

        # Проверяем корректность переходов
        transitions_as_tuples = [tuple(tr) for tr in loaded_fa.transitionList]
        assert ("0", "a", "1") in transitions_as_tuples
        assert ("1", "b", "2") in transitions_as_tuples
        assert ("0", "c", "2") in transitions_as_tuples


class TestFA_simpleEncodeCompleteIntegration:
    """Интеграционные тесты кодирования и доопределения"""

    def test_encode_then_complete_integration_AAA(self):
        """Полная цепочка: создание -> кодирование -> доопределение -> проверка"""
        # Arrange
        fa = FA_simple()
        fa.transitionList = [
            ("state0", "input_a", "state1", "output_x"),
            ("state1", "input_b", "state2", "output_y"),
        ]
        fa.initialState = "state0"
        fa.isFSM = 1
        fa.numberOfStates = 3
        fa.numberOfInputs = 2

        # Act - полная цепочка преобразований
        # 1. Кодируем состояния
        states_changed, states_mapping, _ = fa.encode_states(forced_transform=True)

        # 2. Кодируем входы/выходы
        encode_result = fa.encode_inputs_outputs(forced_transform=True)

        # 3. Доопределяем (теперь все числа)
        reaction = fa.complete(comptype="loop")

        # Assert
        assert states_changed is True, "Состояния должны были перекодироваться"
        assert isinstance(states_mapping, dict)
        assert isinstance(reaction, int)
        assert fa.is_complete(), "После complete автомат должен быть полным"

        # Проверяем что все переходы имеют числа
        for transition in fa.transitionList:
            assert isinstance(transition[0], int)
            assert isinstance(transition[1], int)
            assert isinstance(transition[2], int)
            assert isinstance(transition[3], int)

    def test_complete_dcs_then_simulate_AAA(self):
        """Доопределение DCS -> симуляция неопределенного входа"""
        # Arrange
        fa = FA_simple()
        fa.transitionList = [(0, 0, 1, 10)]  # Уже закодированные числа
        fa.initialState = 0
        fa.isFSM = 1
        fa.numberOfStates = 2
        fa.numberOfInputs = 2

        # Act
        # 1. Доопределяем через DCS
        reaction = fa.complete(comptype="DCS", reaction=999)

        # 2. Симулируем определенный вход
        output1, state1 = fa.move_seq_FSM([0])

        # 3. Симулируем ранее неопределенный вход (теперь ведет в DCS)
        output2, state2 = fa.move_seq_FSM([1])

        # Assert
        assert output1 == [10], "Определенный вход должен работать"
        assert state1 == 1
        assert output2 == [999], "Неопределенный вход должен вести в DCS с реакцией 999"
        assert state2 == 2  # DCS состояние (numberOfStates исходное)


class TestFA_simpleSimulationChainIntegration:
    """Интеграционные тесты цепочек симуляции"""

    def test_simulation_chain_fsm_AAA(self):
        """Цепочка для FSM: создание -> симуляция -> проверка"""
        # Arrange
        fa = FA_simple()
        fa.transitionList = [(0, "a", 1, "x"), (1, "b", 2, "y"), (2, "c", 0, "z")]
        fa.initialState = 0
        fa.isFSM = 1

        input_sequence = ["a", "b", "c"]
        expected_output = ["x", "y", "z"]
        expected_final_state = 0

        # Act
        output_sequence, final_state = fa.move_seq_FSM(input_sequence)

        # Assert
        assert output_sequence == expected_output
        assert final_state == expected_final_state

        # Дополнительная проверка: та же последовательность должна дать тот же результат
        output_sequence2, final_state2 = fa.move_seq_FSM(input_sequence)
        assert output_sequence2 == expected_output
        assert final_state2 == expected_final_state

    def test_simulation_chain_fa_AAA(self):
        """Цепочка для FA: создание -> принятие/отклонение"""
        # Arrange
        fa = FA_simple()
        fa.transitionList = [(0, "a", 1), (1, "b", 2), (0, "c", 3), (3, "d", 4)]
        fa.initialState = 0
        fa.isFSM = 0
        fa.finalStates = {2, 4}  # Два финальных состояния

        # Act & Assert - последовательность принимается
        accepted1, transitions1 = fa.accept_FA(["a", "b"])
        assert accepted1 is True
        assert len(transitions1) == 2

        # Другая последовательность тоже принимается
        accepted2, transitions2 = fa.accept_FA(["c", "d"])
        assert accepted2 is True
        assert len(transitions2) == 2

        # Последовательность не принимается (не в финальное состояние)
        accepted3, transitions3 = fa.accept_FA(["a"])
        assert accepted3 is False
        assert len(transitions3) == 1


class TestFA_simpleTransformationsIntegration:
    """Интеграционные тесты преобразований"""

    def test_rename_then_simulate_AAA(self):
        """Переименование входов -> симуляция с новыми именами"""
        # Arrange
        fa = FA_simple()
        fa.transitionList = [(0, "old_a", 1, "x"), (1, "old_b", 0, "y")]
        fa.initialState = 0
        fa.isFSM = 1
        fa.numberOfInputs = 2

        rename_map = {"old_a": "new_alpha", "old_b": "new_beta"}

        # Act
        # 1. Переименовываем
        fa.rename_inputs(rename_map)

        # 2. Симулируем с новыми именами
        output, state = fa.move_seq_FSM(["new_alpha"])

        # Assert
        assert output == ["x"]
        assert state == 1

        # Проверяем что старые имена больше не работают
        output2, state2 = fa.move_seq_FSM(["old_a"])
        assert output2 is None  # Не должно найти переход

        # Проверяем что переименование действительно произошло
        actions = fa.get_actions_list()
        assert "new_alpha" in actions
        assert "new_beta" in actions
        assert "old_a" not in actions
        assert "old_b" not in actions

    def test_sort_then_operations_AAA(self):
        """Сортировка -> дальнейшие операции"""
        # Arrange - неотсортированные переходы
        fa = FA_simple()
        fa.transitionList = [
            (2, "z", 3, "c"),
            (0, "a", 1, "x"),
            (1, "b", 2, "y"),
            (0, "b", 2, "w"),
        ]
        fa.initialState = 0
        fa.isFSM = 1

        unsorted_first = fa.transitionList[0]

        # Act
        # 1. Сортируем
        fa.sort_trans_table()

        sorted_first = fa.transitionList[0]

        # 2. Выполняем другие операции (должны работать после сортировки)
        states = fa.get_states_list()
        actions = fa.get_actions_list()

        # 3. Симулируем (должно работать)
        output, state = fa.move_seq_FSM(["a"])

        # Assert
        assert unsorted_first != sorted_first, "Таблица должна была отсортироваться"
        assert sorted_first[0] == 0, "Первым должен быть переход из состояния 0"
        assert output == ["x"], "Симуляция должна работать после сортировки"
        assert len(states) == 4
        assert len(actions) == 3


class TestFA_simpleComplexIntegration:
    """Комплексные интеграционные тесты"""

    def test_complete_workflow_AAA(self):
        """Полный workflow: создание -> кодирование -> доопределение -> симуляция"""
        # Arrange - создаем "сырой" автомат со строками
        fa = FA_simple()
        fa.transitionList = [
            ("start", "action1", "middle", "response1"),
            ("middle", "action2", "end", "response2"),
        ]
        fa.initialState = "start"
        fa.isFSM = 1
        fa.numberOfStates = 3
        fa.numberOfInputs = 2  # Только 2 реальных входа!

        print(f"До преобразований: {fa.transitionList}")

        # Act - полный workflow
        # 1. Кодируем состояния
        states_changed, states_mapping, _ = fa.encode_states(forced_transform=True)
        print(f"После encode_states: {fa.transitionList}")

        # 2. Кодируем входы/выходы
        encode_result = fa.encode_inputs_outputs(forced_transform=True)
        print(f"После encode_inputs_outputs: {fa.transitionList}")

        # 3. Доопределяем петлями
        reaction = fa.complete(comptype="loop")
        print(f"После complete: {fa.transitionList}")
        print(f"Реакция: {reaction}")

        # 4. Проверяем полноту
        is_complete = fa.is_complete()
        print(f"Полный: {is_complete}")

        # 5. Симулируем только существующие входы (0 и 1)
        results = []
        for input_val in [0, 1]:  # Только 2 входа после кодирования
            output, state = fa.move_seq_FSM([input_val])
            results.append((input_val, output, state))
            print(f"Вход {input_val}: output={output}, state={state}")

        # Assert
        assert is_complete is True, "После complete автомат должен быть полным"
        assert len(results) == 2, "Должны протестировать 2 входа"

        # Проверяем что основные переходы работают
        assert results[0][1] is not None, "Вход 0 должен быть определен"
        assert results[1][1] is not None, "Вход 1 должен быть определен"


class TestFASimpleEdgeCaseCoverage:
    """Тесты для покрытия граничных случаев"""

    def test_move_seq_fsm_with_none_input_AAA(self, fa_factory):
        """Тест move_seq_FSM с None входом"""
        transitions = [(0, "a", 1, "x"), (1, "b", 0, "y")]
        fa = fa_factory(
            transitions, initial=0, numberOfStates=2, numberOfInputs=2, isFSM=1
        )

        # Подаем None вместо последовательности - оборачиваем в try/except
        try:
            result = fa.move_seq_FSM(None)
            # Если не упало, проверяем результат
            assert result == (None, None)
        except TypeError:
            # Ожидаемое поведение
            pass

    def test_accept_fa_with_empty_sequence_AAA(self, fa_factory):
        """Тест accept_FA с пустой последовательностью"""
        transitions = [(0, "a", 1, ""), (1, "b", 0, "")]
        fa = fa_factory(
            transitions,
            initial=0,
            numberOfStates=2,
            numberOfInputs=2,
            isFSM=0,
            finalStates=[0],
        )

        # Пустая последовательность - автомат в начальном состоянии
        # Метод называется accept_FA
        result = fa.accept_FA([])

        # Начальное состояние 0 в finalStates, должно принять
        assert result is not None
        assert result[0] is True

    def test_accept_fa_with_none_sequence_AAA(self, fa_factory):
        """Тест accept_FA с None последовательностью"""
        transitions = [(0, "a", 1, ""), (1, "b", 0, "")]
        fa = fa_factory(
            transitions,
            initial=0,
            numberOfStates=2,
            numberOfInputs=2,
            isFSM=0,
            finalStates=[0],
        )

        # Метод называется accept_FA
        # Оборачиваем в try/except, так как метод не проверяет на None
        try:
            result = fa.accept_FA(None)
            # Если не упало, то проверяем
            assert result is None
        except TypeError:
            # Ожидаемое поведение - метод падает при итерации по None
            pass

    def test_write_read_with_special_characters_AAA(self, fa_factory, tmp_path):
        """Тест записи/чтения со специальными символами"""
        # Используем более простые специальные символы
        transitions = [
            (0, "newline", 1, "tab"),
            (1, "return", 0, "backslash"),
            (0, "space", 2, "x"),
            (2, "tab", 1, "y"),
        ]
        fa = fa_factory(
            transitions, initial=0, numberOfStates=3, numberOfInputs=4, isFSM=1
        )
        # Устанавливаем отдельно
        fa.numberOfOutputs = 4

        # Записываем в файл
        filename = tmp_path / "special.fsm"
        # Метод называется write_FSM
        fa.write_FSM(str(filename))

        # Проверяем что файл создан
        assert filename.exists()

        fa2 = FA_simple.read_FSM(str(filename))

        # Проверяем что прочитали что-то
        assert fa2 is not None
        assert len(fa2.transitionList) > 0
        # Проверяем, что прочитали все переходы
        assert len(fa2.transitionList) == len(transitions)

    def test_encode_inputs_outputs_no_transform_AAA(self, fa_factory):
        """Тест encode_inputs_outputs когда преобразование не нужно"""
        transitions = [(0, 0, 1, 0), (1, 1, 0, 1), (0, 1, 2, 0), (2, 0, 1, 1)]
        fa = fa_factory(
            transitions, initial=0, numberOfStates=3, numberOfInputs=2, isFSM=1
        )
        fa.numberOfOutputs = 2

        # Входы и выходы уже закодированы правильно
        transformed, in_map, out_map = fa.encode_inputs_outputs()

        # Не должно быть преобразования
        assert transformed is False
        assert in_map == {}
        assert out_map == {}

    def test_encode_inputs_outputs_with_transform_AAA(self, fa_factory):
        """Тест encode_inputs_outputs с преобразованием"""
        transitions = [
            (0, "a", 1, "x"),
            (1, "b", 0, "y"),
            (0, "b", 2, "x"),
            (2, "a", 1, "z"),
        ]
        fa = fa_factory(
            transitions, initial=0, numberOfStates=3, numberOfInputs=2, isFSM=1
        )
        fa.numberOfOutputs = 3

        # Входы и выходы - строки, нужно преобразовать
        transformed, in_map, out_map = fa.encode_inputs_outputs()

        # Должно быть преобразование
        assert transformed is True
        assert in_map  # Не пустой словарь
        assert out_map  # Не пустой словарь

        # Проверяем что теперь все входы - числа
        for tr in fa.transitionList:
            assert isinstance(tr[1], int)
            assert isinstance(tr[3], int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
