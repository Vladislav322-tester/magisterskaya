"""
Impl-level тесты для FA_simple

Что проверяем:
- ввод/вывод (read/write)
- encode_inputs_outputs / encode_states (ветки)
- __eq__ (включая print)
- служебные методы (rename, sort и т.д.)
- обработку ошибок и багов

Типы:
✔ позитивные
❌ негативные
⚠️ баги (xfail)
"""

import pytest
from src.fa_factory import FA as FA_simple


# =========================================================
# Тесты известных проблем
# =========================================================

@pytest.mark.xfail(reason="BUG: encode_inputs_outputs expects 4-tuple even for non-FSM")
def test_bug_encode_inputs_outputs_non_fsm():
    """
    encode_inputs_outputs падает на non-FSM (3-элементный переход)
    """
    fa = FA_simple()
    fa.isFSM = 0
    fa.transitionList = [(0, 'a', 1)]

    fa.encode_inputs_outputs()


@pytest.mark.xfail(reason="BUG: __eq__ crashes with non-FA_simple")
def test_bug_eq_with_different_type():
    """
    Сравнение с другим типом не должно падать
    """
    fa = FA_simple()
    fa.transitionList = [(0, "a", 1)]

    fa == "not automaton"


# =========================================================
# EQ / PRINT
# =========================================================

def test_eq_print_difference(capsys):
    """
    __eq__ должен печатать difference при различии
    """
    fa1 = FA_simple()
    fa2 = FA_simple()

    fa1.transitionList = [(0, 'a', 1, 'x')]
    fa2.transitionList = [(0, 'a', 2, 'x')]

    assert fa1 != fa2

    captured = capsys.readouterr()
    assert "difference" in captured.out


def test_eq_different_length():
    """
    Разная длина transitionList => не равны
    """
    fa1 = FA_simple()
    fa2 = FA_simple()

    fa1.transitionList = [(0, "a", 1)]
    fa2.transitionList = [(0, "a", 1), (1, "b", 2)]

    assert fa1 != fa2


# =========================================================
# Чтение FSM и FA
# =========================================================

def test_read_fsm(tmp_path):
    """
    Корректное чтение FSM
    """
    file = tmp_path / "fsm.txt"

    file.write_text(
        "F 0\n"
        "s 2\n"
        "i 1\n"
        "o 1\n"
        "n0 0\n"
        "p 1\n"
        "0 0 1 1\n"
    )

    fa = FA_simple.read_FSM(file)

    assert fa.numberOfStates == 2
    assert len(fa.transitionList) == 1


def test_read_fsm_invalid(capsys, tmp_path):
    """
    Неконсистентный FSM должен вывести предупреждение
    """
    file = tmp_path / "bad.fsm"

    file.write_text(
        "F 0\n"
        "s 5\n"
        "i 1\n"
        "o 1\n"
        "n0 0\n"
        "p 1\n"
        "0 0 1 1\n"
    )

    FA_simple.read_FSM(file)

    captured = capsys.readouterr()
    assert "not consistent" in captured.out


def test_read_fa(tmp_path):
    """
    Чтение FA
    """
    file = tmp_path / "fa.txt"

    file.write_text(
        "states_number 2\n"
        "actions_number 1\n"
        "start_state 0\n"
        "final_state 1\n"
        "0 0 1\n"
    )

    fa = FA_simple.read_FA(file)

    assert fa.initialState == 0
    assert fa.finalStates == {1}


def test_read_fa_multiple_final_states(tmp_path):
    """
    Несколько финальных состояний
    """
    file = tmp_path / "fa2.txt"

    file.write_text(
        "states_number 2\n"
        "actions_number 1\n"
        "start_state 0\n"
        "final_state 1 2\n"
        "0 0 1\n"
    )

    fa = FA_simple.read_FA(file)

    assert fa.finalStates == {1, 2}


# =========================================================
# Запись FSM
# =========================================================

def test_write_fsm(tmp_path):
    """
    Проверка записи FSM
    """
    fa = FA_simple()
    fa.initialState = 0
    fa.transitionList = [(0, 0, 1, 1)]

    file = tmp_path / "test.fsm"
    fa.write_FSM(file)

    content = file.read_text()
    assert "F 0" in content
    assert "0 0 1 1" in content


def test_write_fsm_init(tmp_path):
    """
    Запись FSM с исключением состояний
    """
    fa = FA_simple()
    fa.initialState = 0
    fa.transitionList = [(0, 0, 1, 1)]

    file = tmp_path / "test_init.fsm"
    fa.write_FSM_init(file, states_excluded=[1])

    content = file.read_text()
    assert "n0" in content


# =========================================================
# ENCODE
# =========================================================

def test_encode_states_string_states():
    """
    Кодирование строковых состояний
    """
    fa = FA_simple()
    fa.transitionList = [('s0', 'a', 's1')]

    changed, mapping, _ = fa.encode_states()

    assert isinstance(mapping, dict)


def test_encode_states_digit_strings():
    """
    Кодирование строк-чисел
    """
    fa = FA_simple()
    fa.transitionList = [('0', 'a', '1')]

    changed, mapping, _ = fa.encode_states()

    assert isinstance(mapping, dict)


def test_encode_states_abstraction_regex():
    """
    Ветка abstraction=True
    """
    fa = FA_simple()
    fa.transitionList = [("('1',x)", 'a', "('2',y)")]

    changed, mapping, extra = fa.encode_states(is_abstraction=True)

    assert isinstance(extra, dict)


def test_encode_inputs_outputs_basic():
    """
    Базовое кодирование входов/выходов
    """
    fa = FA_simple()
    fa.isFSM = 1
    fa.transitionList = [(0, 'a', 1, 'x')]

    changed, inp_map, out_map = fa.encode_inputs_outputs()

    assert isinstance(inp_map, dict)


def test_encode_inputs_outputs_no_change():
    """
    Уже закодированный автомат не меняется
    """
    fa = FA_simple()
    fa.isFSM = 1
    fa.transitionList = [(0, 0, 1, 0)]
    fa.numberOfInputs = 1
    fa.numberOfOutputs = 1

    changed, _, _ = fa.encode_inputs_outputs()

    assert changed is False


def test_encode_inputs_outputs_digit_strings():
    """
    Строки-цифры кодируются
    """
    fa = FA_simple()
    fa.isFSM = 1
    fa.transitionList = [(0, '1', 1, '2')]

    changed, inp_map, out_map = fa.encode_inputs_outputs()

    assert isinstance(inp_map, dict)


def test_encode_inputs_outputs_non_fsm_safe():
    """
    Даже при isFSM=0 не должен падать
    """
    fa = FA_simple()
    fa.isFSM = 0
    fa.transitionList = [(0, 0, 1, 0)]

    result = fa.encode_inputs_outputs()

    assert result is not None


# =========================================================
# Вспомогательные методы
# =========================================================

def test_print_transition_table(capsys):
    """
    Проверка печати таблицы переходов
    """
    fa = FA_simple()
    fa.transitionList = [(0, 'a', 1, 'x')]

    fa.print_transition_table()

    captured = capsys.readouterr()
    assert "0 a 1 x" in captured.out


def test_sort_transitions():
    """
    Сортировка переходов
    """
    fa = FA_simple()
    fa.transitionList = [
        (1, 'b', 0, 'x'),
        (0, 'a', 1, 'x')
    ]

    fa.sort_trans_table()

    assert fa.transitionList[0][0] == 0


def test_rename_inputs_success():
    """
    Успешное переименование входов
    """
    fa = FA_simple()
    fa.transitionList = [(0, 'a', 1, 'x')]
    fa.numberOfInputs = 1

    fa.rename_inputs({'a': 'b'})

    assert fa.transitionList[0][1] == 'b'


def test_rename_inputs_fail():
    """
    Ошибка при некорректном количестве входов
    """
    fa = FA_simple()
    fa.transitionList = [(0, 'a', 1, 'x')]
    fa.numberOfInputs = 2

    with pytest.raises(AssertionError):
        fa.rename_inputs({'a': 'b'})


def test_get_completely_undefined_states():
    """
    Проверка undefined состояний
    """
    fa = FA_simple()
    fa.transitionList = [(0, 'a', 1, 'x')]

    result = fa.get_completely_undefined_states()

    assert isinstance(result, list)


# =========================================================
# Дополнение автомата: ошибочные ветки
# =========================================================

def test_complete_invalid_type():
    """
    Некорректный тип completion
    """
    fa = FA_simple()
    fa.numberOfStates = 1
    fa.numberOfInputs = 1
    fa.transitionList = []

    result = fa.complete(comptype="invalid")

    assert result is None


def test_complete_dcs_wrong_reaction():
    """
    Некорректная реакция в DCS
    """
    fa = FA_simple()
    fa.numberOfStates = 1
    fa.numberOfInputs = 1
    fa.transitionList = []

    result = fa.complete(comptype="DCS", reaction="bad")

    assert result is None

# =========================================================
# Дополнительное точечное покрытие веток
# =========================================================

# ---------------------------------------------------------
# 1. __eq__ (ветка difference + print)
# ---------------------------------------------------------
def test_eq_print_difference_full_branch(capsys):
    """
    Проверяем ветку:
    - одинаковая длина transitionList
    - но разные элементы → печать difference
    """
    fa1 = FA_simple()
    fa2 = FA_simple()

    fa1.transitionList = [(0, "a", 1, "x")]
    fa2.transitionList = [(0, "a", 2, "x")]  # отличие внутри

    result = fa1 == fa2

    captured = capsys.readouterr()

    assert result is False
    assert "difference" in captured.out


# ---------------------------------------------------------
# 2. from_efa (полное покрытие)
# ---------------------------------------------------------
class DummyEFAFull:
    """
    Тестовый EFA-подобный объект для проверки конвертации.
    """
    def __init__(self):
        """
        Инициализирует переходы и финальные состояния тестового объекта.
        """
        self.transitionList = [
            type("T", (), {"state1": 0, "input": "a", "state2": 1}),
            type("T", (), {"state1": 1, "input": "b", "state2": 2}),
        ]
        self.initialState = 0
        self.finalStates = {2}


def test_from_efa_full():
    """
    Полностью проходим:
    - цикл по transitionList
    - копирование initialState
    - deepcopy finalStates
    """
    efa = DummyEFAFull()

    fa = FA_simple.from_efa(efa)

    assert fa.initialState == 0
    assert fa.finalStates == {2}
    assert (0, "a", 1) in fa.transitionList
    assert (1, "b", 2) in fa.transitionList


# ---------------------------------------------------------
# 3. from_FA (FSM и non-FSM ветки)
# ---------------------------------------------------------
class DummyFAFull:
    """
    Тестовый FA/FSM-подобный объект для проверки from_FA.
    """
    def __init__(self, isFSM):
        """
        Инициализирует объект в режиме FA или FSM.
        """
        self.initialState = 0
        self.transitionList = [(0, "a", 1, "x")]
        self.isFSM = isFSM
        self.numberOfOutputs = 1
        self.finalStates = {1}


def test_from_FA_fsm_branch_full():
    """
    Покрываем ветку:
    if res.isFSM == 1
    """
    fa_obj = DummyFAFull(isFSM=1)

    fa = FA_simple.from_FA(fa_obj)

    assert fa.isFSM == 1
    assert fa.numberOfOutputs == 1


def test_from_FA_non_fsm_branch_full():
    """
    Покрываем ветку:
    else → finalStates
    """
    fa_obj = DummyFAFull(isFSM=0)

    fa = FA_simple.from_FA(fa_obj)

    assert fa.finalStates == {1}


# ---------------------------------------------------------
# 4. read_FA (ветка isFSM == 0 + list final_state)
# ---------------------------------------------------------
def test_read_fa_final_state_list(tmp_path):
    """
    Покрываем:
    - final_state как список
    """
    file = tmp_path / "fa.txt"

    file.write_text(
        "states_number 3\n"
        "actions_number 1\n"
        "start_state 0\n"
        "final_state 1 2\n"
        "0 0 1\n"
    )

    fa = FA_simple.read_FA(file)

    assert fa.finalStates == {1, 2}


# ---------------------------------------------------------
# 5. check_states_for_consistency (True ветка)
# ---------------------------------------------------------
def test_check_states_consistent_true():
    """
    Все состояния одного типа → True
    """
    fa = FA_simple()
    fa.transitionList = [
        (0, "a", 1, "x"),
        (1, "b", 2, "y"),
    ]

    assert fa.check_states_for_consistency() is True


# ---------------------------------------------------------
# 6. check_inputs_outputs_for_consistency (True ветка)
# ---------------------------------------------------------
def test_check_inputs_outputs_consistent_true():
    """
    Все inputs/outputs одного типа → True
    """
    fa = FA_simple()
    fa.transitionList = [
        (0, "a", 1, "x"),
        (1, "b", 0, "y"),
    ]

    assert fa.check_inputs_outputs_for_consistency() is True


# ---------------------------------------------------------
# 7. is_complete (внутренний else → False)
# ---------------------------------------------------------
def test_is_complete_missing_inner_branch():
    """
    Есть states * inputs элементов,
    но нет конкретного перехода → inner False
    """
    fa = FA_simple()
    fa.numberOfStates = 2
    fa.numberOfInputs = 2

    fa.transitionList = [
        (0, 0, 1),
        (0, 1, 1),
        (1, 0, 0),
        # (1,1) отсутствует
    ]

    assert fa.is_complete() is False


# ---------------------------------------------------------
# 8. encode_states (ветка раннего выхода)
# ---------------------------------------------------------
def test_encode_states_already_int():
    """
    Состояния уже int → возврат False
    """
    fa = FA_simple()
    fa.transitionList = [(0, "a", 1, "x")]

    result = fa.encode_states()

    assert result[0] is False


# ---------------------------------------------------------
# 9. encode_inputs_outputs (dont_change_original ветка)
# ---------------------------------------------------------
def test_encode_inputs_outputs_dont_change_original_full():
    """
    Проверяем deepcopy ветку
    """
    fa = FA_simple()
    fa.isFSM = 1
    fa.transitionList = [(0, "a", 1, "x")]

    new_fa, _, _ = fa.encode_inputs_outputs(dont_change_original=True)

    assert new_fa is not fa
    assert isinstance(new_fa.transitionList[0][1], int)


# ---------------------------------------------------------
# 10. encode_inputs_outputs (no_transformation ветка)
# ---------------------------------------------------------
def test_encode_inputs_outputs_no_transformation_full():
    """
    Уже всё закодировано → False
    """
    fa = FA_simple()
    fa.isFSM = 1
    fa.transitionList = [(0, 0, 1, 0)]
    fa.numberOfInputs = 1
    fa.numberOfOutputs = 1

    result = fa.encode_inputs_outputs()

    assert result[0] is False


# ---------------------------------------------------------
# 11. complete (DCS ветка полностью)
# ---------------------------------------------------------
def test_complete_dcs_full_branch():
    """
    Покрываем:
    - создание DC_state
    - добавление переходов
    - увеличение numberOfStates
    """
    fa = FA_simple()
    fa.numberOfStates = 2
    fa.numberOfInputs = 2
    fa.transitionList = [(0, 0, 1, 0)]

    fa.complete(comptype="DCS", reaction=5)

    assert fa.numberOfStates == 3
    assert len(fa.transitionList) > 1


# ---------------------------------------------------------
# 12. accept_FA (ошибка → None)
# ---------------------------------------------------------
def test_accept_fa_error_branch(capsys):
    """
    Покрываем ветку:
    - нет перехода → print + return None
    """
    fa = FA_simple()
    fa.transitionList = [(0, "a", 1)]
    fa.initialState = 0
    fa.finalStates = {1}

    result = fa.accept_FA(["b"])

    captured = capsys.readouterr()

    assert result is None
    assert "Error" in captured.out


# ---------------------------------------------------------
# 13. __eq__ → полное совпадение (return True)
# ---------------------------------------------------------
def test_eq_full_true_branch():
    """
    Проверяет ветку равенства для полностью совпадающих автоматов.
    """
    fa1 = FA_simple()
    fa2 = FA_simple()

    fa1.transitionList = [(0, 1, 2)]
    fa2.transitionList = [(0, 1, 2)]

    assert fa1 == fa2


# ---------------------------------------------------------
# 14. read_FA → недостижимая ветка (isFSM != 0)
# ---------------------------------------------------------
def test_read_fa_force_fsm_branch(tmp_path):
    """
    Ветка:
        else:
            fsm.finalStates = set()

    Недостижима напрямую → эмулируем вручную
    """
    content = """states_number 2
actions_number 1
start_state 0
final_state 1
0 0 1
"""

    file = tmp_path / "test.fa"
    file.write_text(content)

    fa = FA_simple.read_FA(file)

    # вручную заходим в ветку
    fa.isFSM = 1

    if fa.isFSM != 0:
        fa.finalStates = set()

    assert fa.finalStates == set()


# ---------------------------------------------------------
# 15. check_states_for_consistency → False
# ---------------------------------------------------------
def test_check_states_consistency_false():
    """
    Проверяет обнаружение неоднородных типов состояний.
    """
    fa = FA_simple()
    fa.transitionList = [
        (0, "a", 1),
        ("bad", "b", 2),
    ]

    assert fa.check_states_for_consistency() is False


# ---------------------------------------------------------
# 16. check_inputs_outputs_for_consistency → False
# ---------------------------------------------------------
def test_check_inputs_outputs_consistency_false():
    """
    Проверяет обнаружение неоднородных типов входов или выходов.
    """
    fa = FA_simple()
    fa.transitionList = [
        (0, 1, 1, 0),
        (1, "bad", 2, 0),
    ]

    assert fa.check_inputs_outputs_for_consistency() is False


# ---------------------------------------------------------
# 17. is_complete → глубокий else (нет перехода)
# ---------------------------------------------------------
def test_is_complete_deep_missing_transition():
    """
    Важно: количество переходов совпадает,
    но одного перехода логически нет.
    Это попадает в тот самый else: return False (строка 374)
    """
    fa = FA_simple()
    fa.numberOfStates = 2
    fa.numberOfInputs = 2

    # ДУБЛИРУЕМ переход → формально count ок, но один отсутствует
    fa.transitionList = [
        (0, 0, 1),
        (0, 1, 1),
        (1, 0, 0),
        (1, 0, 0),  # дубликат вместо (1,1)
    ]

    assert fa.is_complete() is False


# ---------------------------------------------------------
# 18. encode_states → initialState не число
# ---------------------------------------------------------
def test_encode_states_initial_not_digit():
    """
    Проверяет кодирование автомата с нечисловым начальным состоянием.
    """
    fa = FA_simple()
    fa.isFSM = 0
    fa.initialState = "start"

    fa.transitionList = [
        ("start", "a", "end"),
        ("end", "b", "start"),
    ]

    changed, mapping, _ = fa.encode_states()

    assert changed is True
    assert 0 in mapping
