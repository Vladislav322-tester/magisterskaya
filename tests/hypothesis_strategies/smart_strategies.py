"""
Умные стратегии для генерации целых автоматов.
"""

from hypothesis import strategies as st
from typing import Dict
import itertools

# Импортируем базовые стратегии
from .base_strategies import (
    state_strategy,
    simple_input,
    output_strategy,
)


# ============================================
# 1. СТРАТЕГИИ ДЛЯ АВТОМАТОВ
# ============================================

@st.composite
def automaton_data(draw,
                   min_states: int = 1,
                   max_states: int = 5,
                   min_inputs: int = 1,
                   max_inputs: int = 3,
                   is_fsm: bool = True) -> Dict:
    """Генерирует данные для создания автомата."""

    # 1. Генерируем уникальные состояния
    num_states = draw(st.integers(min_value=min_states, max_value=max_states))
    states = []
    states_set = set()

    while len(states) < num_states:
        state = draw(state_strategy())
        if state not in states_set:
            states.append(state)
            states_set.add(state)

    # 2. Генерируем уникальные входы
    num_inputs = draw(st.integers(min_value=min_inputs, max_value=max_inputs))
    inputs = []
    inputs_set = set()

    while len(inputs) < num_inputs:
        inp = draw(simple_input())
        if inp not in inputs_set:
            inputs.append(inp)
            inputs_set.add(inp)

    # 3. Генерируем переходы
    max_possible = num_states * num_inputs
    num_transitions = draw(st.integers(min_value=1, max_value=max_possible))

    transitions = []
    for _ in range(num_transitions):
        from_state = draw(st.sampled_from(states))
        to_state = draw(st.sampled_from(states))
        inp = draw(st.sampled_from(inputs))

        if is_fsm:
            output = draw(output_strategy())
            transition = (from_state, inp, to_state, output)
        else:
            transition = (from_state, inp, to_state)

        transitions.append(transition)

    # 4. Начальное состояние
    initial_state = draw(st.sampled_from(states))

    # 5. Для FA - конечные состояния
    result = {
        'transitions': transitions,
        'initial_state': initial_state,
        'states': states,
        'inputs': inputs,
        'is_fsm': is_fsm
    }

    if not is_fsm:
        num_final = draw(st.integers(min_value=0, max_value=num_states))
        final_states = set(draw(st.lists(
            st.sampled_from(states),
            min_size=num_final,
            max_size=num_final,
            unique=True
        )))
        result['final_states'] = final_states

    return result


@st.composite
def deterministic_automaton_data(draw, is_fsm: bool = True) -> Dict:
    """Генерирует данные для детерминированного автомата."""
    data = draw(automaton_data(
        min_states=2,
        max_states=4,
        min_inputs=1,
        max_inputs=2,
        is_fsm=is_fsm
    ))

    # Делаем детерминированным
    transitions = data['transitions']
    states = data['states']
    inputs = data['inputs']

    used_pairs = set()
    det_transitions = []

    for trans in transitions:
        pair = (trans[0], trans[1])
        if pair not in used_pairs:
            det_transitions.append(trans)
            used_pairs.add(pair)

    data['transitions'] = det_transitions
    return data


@st.composite
def complete_automaton_data(draw, is_fsm: bool = True) -> Dict:
    """Генерирует данные для полного автомата."""
    data = draw(automaton_data(
        min_states=1,
        max_states=3,
        min_inputs=1,
        max_inputs=2,
        is_fsm=is_fsm
    ))

    states = data['states']
    inputs = data['inputs']
    existing = data['transitions']

    # Создаем все возможные пары
    all_pairs = list(itertools.product(states, inputs))

    # Словарь существующих переходов
    trans_map = {(t[0], t[1]): t for t in existing}

    # Добавляем недостающие
    complete_transitions = []
    for from_state, inp in all_pairs:
        if (from_state, inp) in trans_map:
            complete_transitions.append(trans_map[(from_state, inp)])
        else:
            to_state = draw(st.sampled_from(states))
            if is_fsm:
                output = draw(output_strategy())
                complete_transitions.append((from_state, inp, to_state, output))
            else:
                complete_transitions.append((from_state, inp, to_state))

    data['transitions'] = complete_transitions
    return data


@st.composite
def numeric_automaton_data(draw, is_fsm: bool = True) -> Dict:
    """Генерирует данные для числового автомата."""
    num_states = draw(st.integers(min_value=2, max_value=4))
    num_inputs = draw(st.integers(min_value=1, max_value=3))

    states = list(range(num_states))
    inputs = list(range(num_inputs))

    num_transitions = draw(st.integers(min_value=num_states, max_value=num_states * num_inputs))
    transitions = []

    for _ in range(num_transitions):
        from_state = draw(st.sampled_from(states))
        to_state = draw(st.sampled_from(states))
        inp = draw(st.sampled_from(inputs))

        if is_fsm:
            output = draw(st.integers(min_value=0, max_value=2))
            transitions.append((from_state, inp, to_state, output))
        else:
            transitions.append((from_state, inp, to_state))

    result = {
        'transitions': transitions,
        'initial_state': 0,
        'states': states,
        'inputs': inputs,
        'is_fsm': is_fsm
    }

    if not is_fsm:
        num_final = draw(st.integers(min_value=1, max_value=num_states))
        final_states = set(draw(st.lists(
            st.sampled_from(states),
            min_size=num_final,
            max_size=num_final,
            unique=True
        )))
        result['final_states'] = final_states

    return result


# ============================================
# 2. ФУНКЦИЯ ДЛЯ СОЗДАНИЯ АВТОМАТОВ
# ============================================

def create_fa_from_data(data: dict):
    """
    Создает объект FA_simple из данных, сгенерированных стратегиями.
    """
    from src.FA_simple import FA_simple  # Импортируем здесь, чтобы избежать циклических импортов

    fa = FA_simple()
    fa.transitionList = data['transitions']
    fa.initialState = data['initial_state']
    fa.isFSM = 1 if data['is_fsm'] else 0

    # Вычисляем количество состояний и входов
    all_states = set()
    all_inputs = set()
    all_outputs = set()

    for trans in data['transitions']:
        all_states.add(trans[0])
        all_states.add(trans[2])
        all_inputs.add(trans[1])

        if data['is_fsm'] and len(trans) > 3:
            all_outputs.add(trans[3])

    fa.numberOfStates = len(all_states)
    fa.numberOfInputs = len(all_inputs)

    if data['is_fsm']:
        fa.numberOfOutputs = len(all_outputs)
    else:
        fa.finalStates = data.get('final_states', set())

    return fa