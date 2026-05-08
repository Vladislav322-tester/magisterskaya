"""
MODEL TESTS (теоретический уровень)

Проверяем:
- множества состояний
- алфавиты
- полноту
- поведение автомата
- инварианты
- детерминизм
- корректность кодирования

Это основной файл тестов для магистерской
"""

import pytest
from src.fa_factory import FA as FA_simple


# =========================================================
# 1. СОСТОЯНИЯ
# =========================================================

class TestStates:

    def test_states_are_defined_by_transitions(self):
        """Состояния извлекаются из переходов"""
        fa = FA_simple()
        fa.transitionList = [
            ("q0", "a", "q1", "x"),
            ("q1", "b", "q2", "y"),
        ]

        assert set(fa.get_states_list()) == {"q0", "q1", "q2"}

    def test_empty_automaton_has_no_states(self):
        """Пустой автомат не имеет состояний"""
        fa = FA_simple()
        assert fa.get_states_list() == []

    def test_states_with_self_loop(self):
        """Самопетля не дублирует состояние"""
        fa = FA_simple()
        fa.transitionList = [(0, "a", 0, "x")]

        assert set(fa.get_states_list()) == {0}

    def test_invalid_transition_structure(self):
        """Некорректный переход должен вызвать ошибку"""
        fa = FA_simple()
        fa.transitionList = [(0, "a")]

        with pytest.raises(Exception):
            fa.get_states_list()


# =========================================================
# 2. АЛФАВИТ
# =========================================================

class TestAlphabet:

    def test_inputs_extracted_correctly(self):
        fa = FA_simple()
        fa.transitionList = [
            ("q0", "a", "q1", "x"),
            ("q1", "b", "q2", "y"),
        ]

        assert set(fa.get_actions_list()) == {"a", "b"}

    def test_outputs_extracted_correctly(self):
        fa = FA_simple()
        fa.transitionList = [
            ("q0", "a", "q1", "x"),
            ("q1", "b", "q2", "y"),
        ]

        assert set(fa.get_outputs_list()) == {"x", "y"}

    def test_empty_transition_list(self):
        fa = FA_simple()
        assert fa.get_actions_list() == []
        assert fa.get_outputs_list() == []


# =========================================================
# 3. ПОЛНОТА
# =========================================================

class TestCompleteness:

    def test_completion_preserves_existing_transitions(self):
        fa = FA_simple()
        fa.transitionList = [(0, 0, 1, 0)]
        fa.numberOfStates = 2
        fa.numberOfInputs = 2

        before = fa.get_ns_out(0, 0)

        fa.complete(comptype="loop", reaction=9)

        after = fa.get_ns_out(0, 0)

        assert before == after

    def test_complete_automaton(self):
        fa = FA_simple()
        fa.transitionList = [
            (0, 0, 1, 0),
            (0, 1, 0, 1),
            (1, 0, 1, 0),
            (1, 1, 0, 1),
        ]
        fa.numberOfStates = 2
        fa.numberOfInputs = 2

        assert fa.is_complete() is True

    def test_incomplete_automaton(self):
        fa = FA_simple()
        fa.transitionList = [(0, 0, 1, 0)]
        fa.numberOfStates = 2
        fa.numberOfInputs = 2

        assert fa.is_complete() is False

    def test_zero_states(self):
        fa = FA_simple()
        fa.numberOfStates = 0
        fa.numberOfInputs = 0

        assert fa.is_complete() is True


# =========================================================
# 4. КЛАССИФИКАЦИЯ СОСТОЯНИЙ
# =========================================================

class TestStateClassification:

    def test_state_with_no_outgoing_transitions(self):
        fa = FA_simple()
        fa.transitionList = [(0, "a", 1, "x")]

        states = set(fa.get_states_list())
        outgoing = {tr[0] for tr in fa.transitionList}

        no_outgoing = states - outgoing

        assert 1 in no_outgoing

    def test_state_with_no_incoming_transitions(self):
        fa = FA_simple()
        fa.transitionList = [(0, "a", 1, "x")]

        states = set(fa.get_states_list())
        incoming = {tr[2] for tr in fa.transitionList}

        no_incoming = states - incoming

        assert 0 in no_incoming

    def test_isolated_state_detection(self):
        fa = FA_simple()
        fa.transitionList = [(0, "a", 1, "x")]
        fa.numberOfStates = 3

        states = set(range(fa.numberOfStates))
        incoming = {tr[2] for tr in fa.transitionList}
        outgoing = {tr[0] for tr in fa.transitionList}

        isolated = states - incoming - outgoing

        assert 2 in isolated


# =========================================================
# 5. ПОВЕДЕНИЕ
# =========================================================

class TestBehavior:

    def test_outputs_correctness(self):
        fa = FA_simple()
        fa.initialState = 0
        fa.transitionList = [
            (0, "a", 1, "x"),
            (1, "b", 0, "y"),
        ]

        outputs, _ = fa.move_seq_FSM(["a", "b"])

        assert outputs == ["x", "y"]

    def test_state_progression(self):
        fa = FA_simple()
        fa.initialState = 0
        fa.transitionList = [
            (0, "a", 1, "x"),
            (1, "a", 2, "y"),
        ]

        _, state = fa.move_seq_FSM(["a", "a"])

        assert state == 2

    def test_invalid_sequence(self):
        fa = FA_simple()
        fa.initialState = 0
        fa.transitionList = [(0, "a", 1, "x")]

        assert fa.move_seq_FSM(["b"]) == (None, None)

    def test_empty_sequence(self):
        fa = FA_simple()
        fa.initialState = 0

        outputs, state = fa.move_seq_FSM([])

        assert outputs == []
        assert state in [0, "0"]

    def test_long_sequence(self):
        fa = FA_simple()
        fa.initialState = 0
        fa.transitionList = [(0, "a", 0, "x")]

        outputs, _ = fa.move_seq_FSM(["a"] * 100)

        assert len(outputs) == 100


# =========================================================
# 6. get_ns_out
# =========================================================

class TestGetNsOut:

    def test_return_type(self):
        fa = FA_simple()
        fa.transitionList = [(0, "a", 1, "x")]

        result = fa.get_ns_out(0, "a")

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_valid_transition(self):
        fa = FA_simple()
        fa.transitionList = [(0, "a", 1, "x")]

        assert fa.get_ns_out(0, "a") == (1, "x")

    def test_missing_transition(self):
        fa = FA_simple()
        fa.transitionList = [(0, "a", 1, "x")]

        with pytest.raises(Exception):
            fa.get_ns_out(1, "a")


# =========================================================
# 7. ПРИНЯТИЕ
# =========================================================

class TestAcceptance:

    def test_empty_sequence_acceptance(self):
        fa = FA_simple()
        fa.initialState = 0
        fa.finalStates = {0}

        result, _ = fa.accept_FA([])

        assert result is True

    def test_accepting_sequence(self):
        fa = FA_simple()
        fa.transitionList = [(0, "a", 1), (1, "b", 2)]
        fa.initialState = 0
        fa.finalStates = {2}

        result, _ = fa.accept_FA(["a", "b"])

        assert result is True

    def test_rejecting_sequence(self):
        fa = FA_simple()
        fa.transitionList = [(0, "a", 1)]
        fa.initialState = 0
        fa.finalStates = {2}

        result, _ = fa.accept_FA(["a"])

        assert result is False


# =========================================================
# 8. ИНВАРИАНТЫ
# =========================================================

class TestInvariants:

    def test_transitions_count_preserved(self):
        fa = FA_simple()
        fa.transitionList = [
            ("q0", "a", "q1", "x"),
            ("q1", "b", "q2", "y"),
        ]
        fa.isFSM = 1

        before = len(fa.transitionList)

        fa.encode_states(forced_transform=True)

        after = len(fa.transitionList)

        assert before == after

    def test_inputs_outputs_preserved(self):
        fa = FA_simple()
        fa.transitionList = [
            ("q0", "a", "q1", "x"),
            ("q1", "b", "q0", "y"),
        ]
        fa.isFSM = 1

        inputs = set(fa.get_actions_list())
        outputs = set(fa.get_outputs_list())

        fa.encode_states(forced_transform=True)

        assert set(fa.get_actions_list()) == inputs
        assert set(fa.get_outputs_list()) == outputs


# =========================================================
# 9. ДЕТЕРМИНИЗМ
# =========================================================

class TestDeterminism:

    def test_same_input_same_output(self):
        fa = FA_simple()
        fa.transitionList = [
            (0, "a", 1, "x"),
            (1, "b", 0, "y"),
        ]
        fa.initialState = 0

        assert fa.move_seq_FSM(["a", "b"]) == fa.move_seq_FSM(["a", "b"])


# =========================================================
# 10. НЕЗАВИСИМОСТЬ ОТ ПОРЯДКА
# =========================================================

class TestOrderIndependence:

    def test_transition_order_does_not_affect_behavior(self):
        fa1 = FA_simple()
        fa1.transitionList = [(0, "a", 1, "x"), (1, "b", 0, "y")]
        fa1.initialState = 0

        fa2 = FA_simple()
        fa2.transitionList = list(reversed(fa1.transitionList))
        fa2.initialState = 0

        assert fa1.move_seq_FSM(["a", "b"]) == fa2.move_seq_FSM(["a", "b"])
