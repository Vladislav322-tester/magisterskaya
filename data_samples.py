"""
Примеры данных для параметризованных тестов
"""

# ===== FSM ПРИМЕРЫ (4 элемента в переходах) =====
FSM_SAMPLES = [
    # Простой FSM
    (
        [(0, "a", 1, "x"), (1, "b", 0, "y")],  # transitions
        ["a", "b"],  # input_seq
        ["x", "y"],  # expected_output
        0  # expected_final_state
    ),
    # FSM с петлей
    (
        [(0, "a", 0, "x"), (0, "b", 1, "y"), (1, "a", 1, "z"), (1, "b", 0, "w")],
        ["a", "b", "a"],
        ["x", "y", "z"],
        1
    ),
    # FSM с одним состоянием
    (
        [(0, "a", 0, "x"), (0, "b", 0, "y")],
        ["a", "b", "a"],
        ["x", "y", "x"],
        0
    ),
]

# ===== FA ПРИМЕРЫ (3 элемента в переходах) =====
FA_SAMPLES = [
    # Простой FA (принимает)
    (
        [(0, "a", 1), (1, "b", 2)],  # transitions
        {2},  # final_states
        ["a", "b"],  # input_seq
        True  # expected_accept
    ),
    # FA (не принимает)
    (
        [(0, "a", 1), (1, "b", 2)],
        {1},  # final_states
        ["a", "b"],
        False
    ),
    # FA с циклом
    (
        [(0, "a", 1), (1, "b", 0), (0, "c", 2), (2, "a", 2)],
        {2},
        ["a", "b", "c", "a"],
        True
    ),
]

# ===== ТЕСТЫ ДЛЯ get_states_list, get_actions_list =====
GETTERS_SAMPLES = [
    # Для проверки get_states_list
    (
        [(0, "a", 1, "x"), (1, "b", 2, "y")],  # transitions
        {0, 1, 2},  # expected_states
        {"a", "b"},  # expected_actions
        {"x", "y"}   # expected_outputs
    ),
    (
        [("q0", "alpha", "q1", "out1"), ("q1", "beta", "q2", "out2")],
        {"q0", "q1", "q2"},
        {"alpha", "beta"},
        {"out1", "out2"}
    ),
]

# ===== ТЕСТЫ ДЛЯ is_complete =====
COMPLETENESS_SAMPLES = [
    # Полный автомат (2 состояния × 2 входа = 4 перехода)
    (
        [(0, "a", 0, "x"), (0, "b", 1, "y"), (1, "a", 1, "z"), (1, "b", 0, "w")],
        2,  # numberOfStates
        2,  # numberOfInputs
        True  # expected_is_complete
    ),
    # Неполный автомат
    (
        [(0, "a", 1, "x")],
        2,
        2,
        False
    ),
]

# ===== EDGE CASES =====
EDGE_CASES = [
    # Пустой автомат
    ([], [], [], None),

    # Один переход
    ([(0, "a", 1, "x")], ["a"], ["x"], 1),
]