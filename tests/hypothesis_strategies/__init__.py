"""
Пакет со стратегиями Hypothesis для тестирования автоматов.
"""

# Ре-экспортируем ключевые функции
from .base_strategies import (
    numeric_state,
    labeled_state,
    state_strategy,
    simple_input,
    output_strategy,
    transition_strategy,
    can_convert_to_int
)

from .smart_strategies import (
    automaton_data,
    deterministic_automaton_data,
    complete_automaton_data,
    numeric_automaton_data,
    string_automaton_data,
    input_sequence,
    rename_dict,
    create_fa_from_data
)

__all__ = [
    # Из base_strategies
    'numeric_state',
    'labeled_state',
    'state_strategy',
    'simple_input',
    'output_strategy',
    'transition_strategy',
    'can_convert_to_int',

    # Из smart_strategies
    'automaton_data',
    'deterministic_automaton_data',
    'complete_automaton_data',
    'numeric_automaton_data',
    'string_automaton_data',
    'input_sequence',
    'rename_dict',
    'create_fa_from_data',
]