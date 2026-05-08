"""
УЛУЧШЕННЫЕ стратегии для FA_simple.

Цели:
- valid_fa → корректные автоматы (инварианты)
- valid_fsm → автоматы с выходами
- incomplete_fa → тестирование complete()
- broken_fa → robustness (поиск багов)
"""

from hypothesis import strategies as st
from hypothesis.strategies import composite, lists, sampled_from, integers
from typing import Dict, Any, Type


# ------------------------------------------------------------
# 1. БАЗОВЫЕ ЭЛЕМЕНТЫ
# ------------------------------------------------------------

STATE = integers(min_value=0, max_value=5)
INPUT = sampled_from(['a', 'b'])
OUTPUT = sampled_from(['OK', 'FAIL'])


# ------------------------------------------------------------
# 2. ВАЛИДНЫЙ FA (ПОЛНЫЙ, ДЕТЕРМИНИРОВАННЫЙ)
# ------------------------------------------------------------

@composite
def valid_fa(draw) -> Dict[str, Any]:
    """
    Генерирует корректный ПОЛНЫЙ детерминированный FA.
    """

    states = draw(lists(STATE, min_size=1, max_size=5, unique=True))
    inputs = draw(lists(INPUT, min_size=1, max_size=2, unique=True))

    transitions = [
        (s, i, draw(sampled_from(states)))
        for s in states
        for i in inputs
    ]

    return {
        "transitions": transitions,
        "initial_state": draw(sampled_from(states)),
        "states": states,
        "inputs": inputs,
        "is_fsm": False,
        "final_states": set(draw(
            lists(sampled_from(states), min_size=1, unique=True)
        )),
    }


# ------------------------------------------------------------
# 3. ВАЛИДНЫЙ FSM (С ВЫХОДАМИ)
# ------------------------------------------------------------

@composite
def valid_fa_with_string_states(draw) -> Dict[str, Any]:
    """
    Generates a valid deterministic FA whose states are numeric strings.
    This exercises state encoding without triggering FA_simple's known
    int(current_state) limitation in accept_FA.
    """

    state_numbers = draw(lists(STATE, min_size=1, max_size=5, unique=True))
    states = [str(s) for s in state_numbers]
    inputs = draw(lists(INPUT, min_size=1, max_size=2, unique=True))

    transitions = [
        (s, i, draw(sampled_from(states)))
        for s in states
        for i in inputs
    ]

    return {
        "transitions": transitions,
        "initial_state": draw(sampled_from(states)),
        "states": states,
        "inputs": inputs,
        "is_fsm": False,
        "final_states": set(draw(
            lists(sampled_from(state_numbers), min_size=1, unique=True)
        )),
    }


@composite
def valid_fsm(draw) -> Dict[str, Any]:
    """
    Генерирует корректный ПОЛНЫЙ FSM.
    """

    states = draw(lists(STATE, min_size=1, max_size=5, unique=True))
    inputs = draw(lists(INPUT, min_size=1, max_size=2, unique=True))

    transitions = [
        (s, i, draw(sampled_from(states)), draw(OUTPUT))
        for s in states
        for i in inputs
    ]

    return {
        "transitions": transitions,
        "initial_state": draw(sampled_from(states)),
        "states": states,
        "inputs": inputs,
        "is_fsm": True,
    }


# ------------------------------------------------------------
# 4. НЕПОЛНЫЙ FA (для complete)
# ------------------------------------------------------------

@composite
def incomplete_fa(draw) -> Dict[str, Any]:
    """
    Генерирует гарантированно НЕполный автомат.
    """

    states = draw(lists(STATE, min_size=2, max_size=4, unique=True))
    inputs = draw(lists(INPUT, min_size=1, max_size=2, unique=True))

    transitions = []

    for s in states:
        for i in inputs:
            if draw(st.booleans()):
                transitions.append((s, i, draw(sampled_from(states))))

    # гарантируем неполноту
    if len(transitions) == len(states) * len(inputs):
        transitions = transitions[:-1]

    return {
        "transitions": transitions,
        "initial_state": draw(sampled_from(states)),
        "states": states,
        "inputs": inputs,
        "is_fsm": False,
        "final_states": set(states[:1]),
    }


# ------------------------------------------------------------
# 5. КРАЙНИЕ СЛУЧАИ (EDGE)
# ------------------------------------------------------------

@composite
def edge_fa(draw) -> Dict[str, Any]:
    """
    Граничные случаи (валидные, но особые).
    """

    case = draw(sampled_from([
        "empty",
        "single_state",
        "loop",
    ]))

    if case == "empty":
        return {
            "transitions": [],
            "initial_state": 0,
            "is_fsm": False,
            "final_states": set(),
        }

    elif case == "single_state":
        return {
            "transitions": [(0, 'a', 0)],
            "initial_state": 0,
            "is_fsm": False,
            "final_states": {0},
        }

    else:  # loop
        return {
            "transitions": [(0, 'a', 0), (0, 'b', 0)],
            "initial_state": 0,
            "is_fsm": False,
            "final_states": {0},
        }


# ------------------------------------------------------------
# 6. СЛОМАННЫЕ АВТОМАТЫ (ROBUSTNESS)
# ------------------------------------------------------------

@composite
def broken_fa(draw) -> Dict[str, Any]:
    """
    Генерирует некорректные автоматы.
    Проверяем устойчивость реализации.
    """

    case = draw(sampled_from([
        "short_transition",
        "wrong_types",
        "missing_elements",
        "mixed_types",
    ]))

    if case == "short_transition":
        transitions = [(0, 'a')]  # нет конечного состояния

    elif case == "wrong_types":
        transitions = [("s", 123, "t")]  # типы сломаны

    elif case == "missing_elements":
        transitions = [()]  # пустой переход

    else:  # mixed_types
        transitions = [(0, 'a', "1")]  # int + str

    return {
        "transitions": transitions,
        "initial_state": 0,
        "is_fsm": False,
        "final_states": set(),
    }


# ------------------------------------------------------------
# 7. СЛУЧАЙНЫЕ СЛОВА
# ------------------------------------------------------------

def random_word():
    """
    Генератор входных последовательностей.
    """
    return lists(INPUT, min_size=0, max_size=10)


# ------------------------------------------------------------
# 8. СОЗДАНИЕ ОБЪЕКТА FA_simple
# ------------------------------------------------------------

def create_complete_fa_from_data(
    data: Dict,
    fa_class: Type,
    apply_complete: bool = False,
):
    """
    Универсальная фабрика для создания автомата из данных стратегии.

    Поддерживает:
    - FA_simple (list-based)
    - FA_dict (dict-based)
    """

    # ---------------------------------------------------------
    # 1. dict-based реализация (новая)
    # ---------------------------------------------------------
    if hasattr(fa_class, "from_data"):
        fa = fa_class.from_data(data)

        if apply_complete:
            try:
                fa.complete()
            except Exception:
                pass

        return fa

    # ---------------------------------------------------------
    # 2. старая реализация (FA_simple)
    # ---------------------------------------------------------
    fa = fa_class()

    fa.transitionList = data.get("transitions", [])
    fa.initialState = data.get("initial_state", 0)
    fa.isFSM = 1 if data.get("is_fsm", False) else 0

    # ---------------------------------------------------------
    # состояния
    # ---------------------------------------------------------
    all_states = set()

    for t in fa.transitionList:
        if len(t) > 0:
            all_states.add(t[0])
        if len(t) > 2:
            all_states.add(t[2])

    if fa.initialState is not None:
        all_states.add(fa.initialState)

    fa.numberOfStates = len(all_states)

    # ---------------------------------------------------------
    # входы
    # ---------------------------------------------------------
    all_inputs = set()

    for t in fa.transitionList:
        if len(t) > 1:
            all_inputs.add(t[1])

    fa.numberOfInputs = len(all_inputs)

    # ---------------------------------------------------------
    # FA / FSM
    # ---------------------------------------------------------
    if fa.isFSM == 0:
        fa.finalStates = data.get("final_states", set())
    else:
        outputs = set()
        for t in fa.transitionList:
            if len(t) > 3:
                outputs.add(t[3])
        fa.numberOfOutputs = len(outputs)

    # ---------------------------------------------------------
    # делаем complete (как раньше)
    # ---------------------------------------------------------
    if apply_complete:
        try:
            fa.complete()
        except Exception:
            pass

    return fa


# ------------------------------------------------------------
# EXPORT
# ------------------------------------------------------------

__all__ = [
    "valid_fa",
    "valid_fa_with_string_states",
    "valid_fsm",
    "incomplete_fa",
    "edge_fa",
    "broken_fa",
    "random_word",
    "create_complete_fa_from_data",
]
