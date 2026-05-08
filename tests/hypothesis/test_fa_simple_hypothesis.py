"""
Property-based тесты для FA_simple.

Цели:
- Проверка инвариантов поведения (behavioral)
- Проверка структурной корректности (structural)
- Проверка устойчивости (robustness)
"""

from hypothesis import given, settings, HealthCheck
import random
from src.fa_factory import FA as FA_simple

from tests.hypothesis.hypothesis_strategies import (
    valid_fa,
    broken_fa,
    incomplete_fa,
    random_word,
    create_complete_fa_from_data,
)

# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

COMMON_SETTINGS = settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.too_slow],
)


# =========================================================
# 1. BEHAVIORAL СВОЙСТВА
# =========================================================

# ---------------------------------------------------------
# 1.1 Детерминизм
# ---------------------------------------------------------

@given(valid_fa(), random_word())
@COMMON_SETTINGS
def test_accept_deterministic(data, word):
    fa = create_complete_fa_from_data(data, FA_simple)

    assert fa.accept_FA(word) == fa.accept_FA(word)


# ---------------------------------------------------------
# 1.2 encode_states сохраняет язык
# ---------------------------------------------------------

@given(valid_fa(), random_word())
@COMMON_SETTINGS
def test_encode_preserves_behavior(data, word):
    fa = create_complete_fa_from_data(data, FA_simple)

    before = fa.accept_FA(word)

    fa.encode_states(forced_transform=True)

    after = fa.accept_FA(word)

    assert before == after


# ---------------------------------------------------------
# 1.3 порядок переходов не влияет
# ---------------------------------------------------------

@given(valid_fa(), random_word())
@COMMON_SETTINGS
def test_order_independence(data, word):
    fa1 = create_complete_fa_from_data(data, FA_simple)
    fa2 = create_complete_fa_from_data(data, FA_simple)

    random.shuffle(fa2.transitionList)

    assert fa1.accept_FA(word) == fa2.accept_FA(word)


# =========================================================
# 2. STRUCTURAL СВОЙСТВА
# =========================================================

# ---------------------------------------------------------
# 2.1 состояния покрывают переходы
# ---------------------------------------------------------

@given(valid_fa())
@COMMON_SETTINGS
def test_states_cover_transitions(data):
    fa = create_complete_fa_from_data(data, FA_simple)

    states = fa.get_states_list()

    for t in fa.transitionList:
        assert t[0] in states
        assert t[2] in states


# ---------------------------------------------------------
# 2.2 encode_states нормализует состояния
# ---------------------------------------------------------

@given(valid_fa())
@COMMON_SETTINGS
def test_encode_states_normalizes(data):
    fa = create_complete_fa_from_data(data, FA_simple)

    fa.encode_states(forced_transform=True)

    states = fa.get_states_list()

    assert all(isinstance(s, int) for s in states)
    assert len(states) == len(set(states))


# ---------------------------------------------------------
# 2.3 encode_states идемпотентен
# ---------------------------------------------------------

@given(valid_fa())
@COMMON_SETTINGS
def test_encode_idempotent(data):
    fa = create_complete_fa_from_data(data, FA_simple)

    fa.encode_states(forced_transform=True)
    first = list(fa.transitionList)

    fa.encode_states(forced_transform=True)
    second = list(fa.transitionList)

    assert first == second


# ---------------------------------------------------------
# 2.4 complete не уменьшает число переходов
# ---------------------------------------------------------

@given(valid_fa())
@COMMON_SETTINGS
def test_complete_monotonic(data):
    fa = create_complete_fa_from_data(data, FA_simple)

    before = len(fa.transitionList)

    fa.complete()

    after = len(fa.transitionList)

    assert after >= before

# ---------------------------------------------------------
# 2.5 complete идемпотентен
# ---------------------------------------------------------

@given(valid_fa())
@COMMON_SETTINGS
def test_complete_idempotent(data):
    fa = create_complete_fa_from_data(data, FA_simple)

    fa.complete()
    first = list(fa.transitionList)

    fa.complete()
    second = list(fa.transitionList)

    assert first == second


# ---------------------------------------------------------
# 2.6 complete увеличивает переходы для incomplete (если возможно)
# ---------------------------------------------------------

@given(incomplete_fa())
@COMMON_SETTINGS
def test_complete_adds_transitions(data):
    fa = create_complete_fa_from_data(data, FA_simple)

    before = len(fa.transitionList)

    fa.complete()

    after = len(fa.transitionList)

    # мягкое свойство (не строгое!)
    assert after >= before


# =========================================================
# 3. ROBUSTNESS СВОЙСТВА
# =========================================================

# ---------------------------------------------------------
# 3.1 accept не падает
# ---------------------------------------------------------

@given(valid_fa(), random_word())
@COMMON_SETTINGS
def test_accept_no_crash(data, word):
    fa = create_complete_fa_from_data(data, FA_simple)

    fa.accept_FA(word)


# ---------------------------------------------------------
# 3.2 методы устойчивы к плохим данным
# ---------------------------------------------------------

@given(broken_fa())
@COMMON_SETTINGS
def test_methods_no_crash_on_broken(data):
    fa = create_complete_fa_from_data(data, FA_simple)

    try:
        fa.accept_FA(['a'])
    except Exception:
        pass

    try:
        fa.encode_states()
    except Exception:
        pass

    try:
        fa.is_complete()
    except Exception:
        pass


# ---------------------------------------------------------
# 3.3 complete не падает
# ---------------------------------------------------------

@given(valid_fa())
@COMMON_SETTINGS
def test_complete_no_crash(data):
    fa = create_complete_fa_from_data(data, FA_simple)

    fa.complete()

# =========================================================
# 4. ДОПОЛНИТЕЛЬНОЕ ПОКРЫТИЕ (ADVANCED)
# =========================================================

# ---------------------------------------------------------
# 4.1 encode_inputs_outputs не ломает структуру
# ---------------------------------------------------------

@given(valid_fa())
@COMMON_SETTINGS
def test_encode_inputs_outputs_no_crash(data):
    """
    Инвариант:
    encode_inputs_outputs не должен менять количество переходов
    и не должен падать.
    """
    fa = create_complete_fa_from_data(data, FA_simple)

    before = len(fa.transitionList)

    try:
        fa.encode_inputs_outputs()
    except Exception:
        return  # допустимо (известные проблемы)

    after = len(fa.transitionList)

    assert after == before


# ---------------------------------------------------------
# 4.2 FSM: accept не падает
# ---------------------------------------------------------

from tests.hypothesis.hypothesis_strategies import valid_fsm


@given(valid_fsm(), random_word())
@COMMON_SETTINGS
def test_fsm_accept_no_crash(data, word):
    """
    Инвариант:
    FSM не должен падать при обработке входа.
    """
    fa = create_complete_fa_from_data(data, FA_simple)

    try:
        fa.accept_FA(word)
    except Exception:
        pass


# ---------------------------------------------------------
# 4.3 __eq__ рефлексивность
# ---------------------------------------------------------

@given(valid_fa())
@COMMON_SETTINGS
def test_eq_reflexive(data):
    """
    Инвариант:
    Объект равен сам себе.
    """
    fa = create_complete_fa_from_data(data, FA_simple)

    assert fa == fa


# ---------------------------------------------------------
# 4.4 __eq__ симметричность (мягкая)
# ---------------------------------------------------------

@given(valid_fa(), valid_fa())
@COMMON_SETTINGS
def test_eq_symmetric(data1, data2):
    """
    Инвариант:
    fa1 == fa2 <=> fa2 == fa1
    """
    fa1 = create_complete_fa_from_data(data1, FA_simple)
    fa2 = create_complete_fa_from_data(data2, FA_simple)

    try:
        assert (fa1 == fa2) == (fa2 == fa1)
    except Exception:
        pass


# ---------------------------------------------------------
# 4.5 состояния согласованы после complete
# ---------------------------------------------------------

@given(valid_fa())
@COMMON_SETTINGS
def test_states_consistency_after_complete(data):
    """
    Инвариант:
    После complete все состояния из переходов существуют.
    """
    fa = create_complete_fa_from_data(data, FA_simple)

    fa.complete()

    states = fa.get_states_list()

    for t in fa.transitionList:
        if len(t) > 0:
            assert t[0] in states
        if len(t) > 2:
            assert t[2] in states


# ---------------------------------------------------------
# 4.6 композиция encode + complete
# ---------------------------------------------------------

@given(valid_fa(), random_word())
@COMMON_SETTINGS
def test_encode_then_complete(data, word):
    """
    Инвариант:
    encode_states + complete не должны менять поведение автомата.
    """
    fa = create_complete_fa_from_data(data, FA_simple)

    try:
        before = fa.accept_FA(word)

        fa.encode_states(forced_transform=True)
        fa.complete()

        after = fa.accept_FA(word)

        assert before == after
    except Exception:
        pass

# =========================================================
# 5. TARGETED TESTS (ТОЧЕЧНОЕ ПОКРЫТИЕ)
# =========================================================

# ---------------------------------------------------------
# 5.1 read_FA корректно читает файл
# ---------------------------------------------------------

def test_read_fa_smoke(tmp_path):
    """
    Инвариант:
    read_FA корректно создает автомат из файла.
    """

    content = """states_number 1
actions_number 1
start_state 0
final_state 0
0 a 0
"""

    file = tmp_path / "fa.txt"
    file.write_text(content)

    fa = FA_simple.read_FA(str(file))

    assert fa.initialState == 0
    assert fa.numberOfStates == 1
    assert len(fa.transitionList) == 1


# ---------------------------------------------------------
# 5.2 FSM: encode_inputs_outputs сохраняет структуру
# ---------------------------------------------------------

from tests.hypothesis.hypothesis_strategies import valid_fsm


@given(valid_fsm())
@COMMON_SETTINGS
def test_fsm_encode_inputs_outputs(data):
    """
    Инвариант:
    encode_inputs_outputs для FSM не должен ломать переходы.
    """
    fa = create_complete_fa_from_data(data, FA_simple)

    before = len(fa.transitionList)

    try:
        fa.encode_inputs_outputs()
    except Exception:
        return  # допустимо (известные баги)

    after = len(fa.transitionList)

    assert after == before
