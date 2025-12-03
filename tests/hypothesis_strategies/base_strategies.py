"""
Базовые стратегии Hypothesis для генерации элементов автоматов.
"""

from hypothesis import strategies as st
from typing import Union, Tuple
import string


# ============================================
# 1. СТРАТЕГИИ ДЛЯ СОСТОЯНИЙ
# ============================================

@st.composite
def numeric_state(draw, min_value: int = 0, max_value: int = 10) -> int:
    """Генерирует состояние как целое число."""
    return draw(st.integers(min_value=min_value, max_value=max_value))


@st.composite
def labeled_state(draw) -> str:
    """Генерирует состояние с текстовой меткой."""
    prefix = draw(st.sampled_from(['q', 's', 'state_', '']))
    number = draw(st.integers(min_value=0, max_value=99))
    suffix = draw(st.sampled_from(['', "'", '*', '_final']))
    return f"{prefix}{number}{suffix}"


@st.composite
def state_strategy(draw, allow_numeric: bool = True, allow_labeled: bool = True) -> Union[int, str]:
    """Умная стратегия выбора типа состояния."""
    strategies = []
    if allow_numeric:
        strategies.append(numeric_state())
    if allow_labeled:
        strategies.append(labeled_state())
    if not strategies:
        raise ValueError("Должен быть разрешен хотя бы один тип состояний")
    return draw(st.one_of(*strategies))


# ============================================
# 2. СТРАТЕГИИ ДЛЯ ВХОДНЫХ СИМВОЛОВ
# ============================================

@st.composite
def simple_input(draw) -> Union[int, str]:
    """Генерирует входной символ (действие)."""
    return draw(st.one_of(
        st.integers(min_value=0, max_value=9),
        st.characters(min_codepoint=97, max_codepoint=102),  # a-f
        st.sampled_from(['0', '1', 'start', 'reset', 'next', 'prev'])
    ))


# ============================================
# 3. СТРАТЕГИИ ДЛЯ ВЫХОДНЫХ СИМВОЛОВ
# ============================================

@st.composite
def output_strategy(draw) -> Union[int, str]:
    """Генерирует выходной символ."""
    return draw(st.one_of(
        st.integers(min_value=0, max_value=9),
        st.sampled_from(['OK', 'SUCCESS', 'ACCEPT', 'WAIT', 'ERROR', ''])
    ))


# ============================================
# 4. СТРАТЕГИИ ДЛЯ ПЕРЕХОДОВ
# ============================================

@st.composite
def transition_strategy(draw, is_fsm: bool = True) -> Tuple:
    """Генерирует корректный переход автомата."""
    use_numeric = draw(st.booleans())

    if use_numeric:
        state_from = draw(numeric_state())
        state_to = draw(numeric_state())
    else:
        state_from = draw(labeled_state())
        state_to = draw(labeled_state())

    input_sym = draw(simple_input())

    if is_fsm:
        output_sym = draw(output_strategy())
        return (state_from, input_sym, state_to, output_sym)
    else:
        return (state_from, input_sym, state_to)


# ============================================
# 5. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def can_convert_to_int(value) -> bool:
    """Проверяет, можно ли значение преобразовать в int."""
    try:
        int(str(value))
        return True
    except (ValueError, TypeError):
        return False


def get_state_type(states) -> str:
    """Определяет тип состояний: 'int', 'str', или 'mixed'."""
    types = set(type(state).__name__ for state in states)
    if len(types) == 1:
        return list(types)[0]
    return 'mixed'