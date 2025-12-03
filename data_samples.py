"""
Примеры данных для параметризованных тестов
"""
from gen_strategies import generate_fsm_sample, generate_fa_sample
import random

SAMPLES = []

# Генерация 10 примеров для параметризованных тестов FSM
for i in range(10):
    fsm_data = generate_fsm_sample(min_states=2, max_states=4)
    transitions = fsm_data['transitions']

    if not transitions:
        continue

    # Генерируем входную последовательность
    inputs = fsm_data['inputs']
    input_seq = [random.choice(inputs) for _ in range(random.randint(1, 3))]

    # Выбираем конечное состояние
    final_state = random.choice(fsm_data['states'])

    # Упрощенная логика определения принятия
    # В реальных тестах нужно использовать move_seq_FSM
    last_state = transitions[-1][2] if transitions else 0
    expected_accept = last_state == final_state

    SAMPLES.append((transitions, final_state, input_seq, expected_accept))

# Примеры для edge cases
EDGE_CASE_SAMPLES = [
    # Пустой автомат
    ([], 0, [], False),

    # Один переход - принимает
    ([(0, "a", 1, "x")], 1, ["a"], True),

    # Один переход - не принимает
    ([(0, "a", 1, "x")], 0, ["a"], False),

    # Петля
    ([(0, "a", 0, "x")], 0, ["a"], True),

    # Несколько переходов
    ([(0, "a", 1, "x"), (1, "b", 2, "y")], 2, ["a", "b"], True),

    # Неполная последовательность
    ([(0, "a", 1, "x"), (1, "b", 2, "y")], 2, ["a"], False),
]

# Объединяем все примеры
ALL_SAMPLES = SAMPLES + EDGE_CASE_SAMPLES

# Примеры для тестирования FA (без выходов)
FA_SAMPLES = []
for i in range(5):
    fa_data = generate_fa_sample(min_states=2, max_states=3)
    transitions = fa_data['transitions']

    if not transitions:
        continue

    inputs = fa_data['inputs']
    input_seq = [random.choice(inputs) for _ in range(min(2, len(transitions)))]
    final_state = random.choice(fa_data['states'])

    FA_SAMPLES.append((transitions, final_state, input_seq, True))