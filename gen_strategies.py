"""
Генераторы тестовых данных с использованием Hypothesis
"""
from hypothesis import strategies as st
import random

# Базовые стратегии
state_strategy = st.integers(min_value=0, max_value=10) | st.text(
    alphabet=st.characters(min_codepoint=65, max_codepoint=90),  # A-Z
    min_size=1,
    max_size=3
)

input_strategy = st.text(
    alphabet=st.characters(min_codepoint=97, max_codepoint=122),  # a-z
    min_size=1,
    max_size=2
)

output_strategy = st.text(
    alphabet=st.characters(min_codepoint=97, max_codepoint=122),  # a-z
    min_size=1,
    max_size=2
)

# Стратегия для генерации одного перехода FSM
fsm_transition_strategy = st.tuples(
    state_strategy,
    input_strategy,
    state_strategy,
    output_strategy
)

# Стратегия для генерации одного перехода FA (без выхода)
fa_transition_strategy = st.tuples(
    state_strategy,
    input_strategy,
    state_strategy
)

# Стратегия для генерации FSM
fsm_strategy = st.lists(fsm_transition_strategy, min_size=1, max_size=20)

# Стратегия для генерации FA
fa_strategy = st.lists(fa_transition_strategy, min_size=1, max_size=20)

# Стратегия для генерации конечных состояний
final_state_strategy = state_strategy

# Стратегия для генерации входных последовательностей
input_sequence_strategy = st.lists(
    input_strategy,
    min_size=1,
    max_size=10
)


def generate_fsm_sample(min_states=2, max_states=5, min_inputs=1, max_inputs=3):
    """Генерация одного примера FSM"""
    states = list(range(random.randint(min_states, max_states)))
    inputs = [chr(97 + i) for i in range(random.randint(min_inputs, max_inputs))]  # a, b, c...
    outputs = ["x", "y", "z", "w"]

    transitions = []
    for state in states:
        for inp in inputs:
            if random.random() > 0.3:  # 70% вероятности создать переход
                next_state = random.choice(states)
                output = random.choice(outputs)
                transitions.append((state, inp, next_state, output))

    return {
        'transitions': transitions,
        'states': states,
        'inputs': inputs,
        'outputs': outputs
    }


def generate_fa_sample(min_states=2, max_states=5, min_inputs=1, max_inputs=3):
    """Генерация одного примера FA"""
    states = list(range(random.randint(min_states, max_states)))
    inputs = [chr(97 + i) for i in range(random.randint(min_inputs, max_inputs))]

    transitions = []
    for state in states:
        for inp in inputs:
            if random.random() > 0.4:  # 60% вероятности создать переход
                next_state = random.choice(states)
                transitions.append((state, inp, next_state))

    return {
        'transitions': transitions,
        'states': states,
        'inputs': inputs
    }


def get_sample_fsm():
    """Получить готовый пример FSM"""
    return [
        (0, "a", 1, "x"),
        (1, "b", 0, "y"),
        (0, "b", 2, "z"),
        (2, "a", 1, "w"),
        (2, "b", 2, "v")
    ]


def get_sample_fa():
    """Получить готовый пример FA"""
    return [
        (0, "a", 1),
        (1, "b", 2),
        (2, "a", 0),
        (0, "c", 2),
        (1, "c", 0)
    ]