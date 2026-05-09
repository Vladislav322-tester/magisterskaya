"""Теоретически ориентированная реализация детерминированного автомата.

FA_dict независим от legacy-реализации FA_simple и моделирует partial DFA:

    Q, Sigma, delta, q0, F

Функция переходов хранится как словарь с ключом (состояние, вход).
Публичные методы сохраняют минимальную совместимость с тестовой
инфраструктурой, но основное поведение задается DFA-семантикой.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any


class FA_dict:
    """
    Детерминированный конечный автомат с хранением переходов в словаре.
    """
    def __init__(self):
        """
        Инициализирует пустой автомат и служебные поля совместимости.
        """
        self.states: set[Any] = set()
        self.inputs: set[Any] = set()
        self.transitions: dict[tuple[Any, Any], Any] = {}
        self.outputs: dict[tuple[Any, Any], Any] = {}
        self._order: list[tuple[Any, Any]] = []
        self._malformed_transitions: list[tuple[Any, ...]] = []

        self.initialState: Any = 0
        self.finalStates: set[Any] = set()
        self.isFSM = 0
        self.numberOfStates = 0
        self.numberOfInputs = 0
        self.numberOfOutputs = 0

    # ---------------------------------------------------------
    # Создание автомата
    # ---------------------------------------------------------

    @classmethod
    def from_data(cls, data):
        """
        Создает автомат из словаря данных, используемого Hypothesis-стратегиями.
        """
        fa = cls()
        fa.states = set(data.get("states", []))
        fa.inputs = set(data.get("inputs", []))
        fa.initialState = data.get("initial_state", 0)
        fa.finalStates = set(data.get("final_states", []))
        fa.isFSM = 1 if data.get("is_fsm", False) else 0
        fa.numberOfStates = len(fa.states)
        fa.numberOfInputs = len(fa.inputs)
        fa.transitionList = data.get("transitions", [])
        fa._sync_declared_sizes()
        return fa

    @classmethod
    def from_efa(cls, efa):
        """
        Создает DFA-объект из EFA-подобного объекта для совместимости тестов.
        """
        fa = cls()
        fa.initialState = getattr(efa, "initialState", 0)
        fa.finalStates = set(getattr(efa, "finalStates", set()))
        transitions = []
        for tr in getattr(efa, "transitionList", []):
            transitions.append((tr.state1, tr.input, tr.state2))
        fa.transitionList = transitions
        return fa

    @classmethod
    def from_FA(cls, other):
        """
        Создает DFA-объект из другого FA/FSM-подобного объекта.
        """
        fa = cls()
        fa.initialState = getattr(other, "initialState", 0)
        fa.finalStates = set(getattr(other, "finalStates", set()))
        fa.isFSM = getattr(other, "isFSM", 0)
        fa.numberOfOutputs = getattr(other, "numberOfOutputs", 0)
        fa.transitionList = list(getattr(other, "transitionList", []))
        return fa

    # ---------------------------------------------------------
    # Совместимое представление переходов
    # ---------------------------------------------------------

    @property
    def transitionList(self):
        """
        Возвращает переходы в legacy-формате списка.
        """
        result = []
        result.extend(self._malformed_transitions)
        for key in self._order:
            state, symbol = key
            next_state = self.transitions[key]
            if self.isFSM or key in self.outputs:
                result.append((state, symbol, next_state, self.outputs.get(key, 0)))
            else:
                result.append((state, symbol, next_state))
        return result

    @transitionList.setter
    def transitionList(self, transitions):
        """
        Загружает переходы из legacy-списка в словарную модель DFA.
        """
        self.transitions = {}
        self.outputs = {}
        self._order = []
        self._malformed_transitions = []

        for tr in transitions or []:
            if len(tr) < 3:
                self._malformed_transitions.append(tuple(tr))
                continue
            state, symbol, next_state = tr[:3]
            output = tr[3] if len(tr) >= 4 else None
            self._add_transition(state, symbol, next_state, output)

        self._sync_declared_sizes()

    def _add_transition(self, state, symbol, next_state, output=None):
        """
        Добавляет переход, проверяя детерминизм по паре состояние-вход.
        """
        key = (state, symbol)
        if key in self.transitions:
            same_next = self.transitions[key] == next_state
            same_output = self.outputs.get(key) == output
            if not (same_next and same_output):
                raise ValueError(f"Nondeterministic transition for {key}")
            return

        self.transitions[key] = next_state
        if output is not None:
            self.outputs[key] = output
            self.isFSM = 1
        self._order.append(key)
        self.states.update([state, next_state])
        self.inputs.add(symbol)

    def _sync_declared_sizes(self):
        """
        Синхронизирует объявленные размеры с фактическими множествами автомата.
        """
        self.numberOfStates = max(self.numberOfStates, len(self.states))
        self.numberOfInputs = max(self.numberOfInputs, len(self.inputs))
        self.numberOfOutputs = max(self.numberOfOutputs, len(set(self.outputs.values())))

    # ---------------------------------------------------------
    # Формальные вспомогательные методы DFA
    # ---------------------------------------------------------

    def _all_states(self):
        """
        Возвращает множество состояний Q с учетом явно заданного размера.
        """
        states = set(self.states)
        if (
            self.numberOfStates
            and self._states_are_integer_like()
            and (not states or states.issubset(set(range(self.numberOfStates))))
        ):
            states.update(range(self.numberOfStates))
        return states

    def _all_inputs(self):
        """
        Возвращает входной алфавит Sigma с учетом явно заданного размера.
        """
        inputs = set(self.inputs)
        if self.numberOfInputs and (not inputs or all(isinstance(i, int) for i in inputs)):
            inputs.update(range(self.numberOfInputs))
        return inputs

    def _states_are_integer_like(self):
        """
        Проверяет, можно ли трактовать состояния как целочисленный диапазон.
        """
        if not self.states:
            return True
        return all(isinstance(s, int) for s in self.states)

    def _lookup_key(self, state, symbol):
        """
        Находит ключ перехода для текущего состояния и входного символа.
        """
        key = (state, symbol)
        if key in self.transitions:
            return key
        return None

    def _is_final(self, state):
        """
        Проверяет, принадлежит ли состояние множеству допускающих состояний F.
        """
        if state in self.finalStates:
            return True
        try:
            if int(state) in self.finalStates:
                return True
        except (TypeError, ValueError):
            pass
        return str(state) in self.finalStates

    def _fresh_sink_state(self):
        """
        Выбирает новое имя для sink/dead state при дополнении автомата.
        """
        states = self._all_states()
        if not states or all(isinstance(s, int) for s in states):
            return max(states, default=-1) + 1

        sink = "__sink__"
        while sink in states:
            sink += "_"
        return sink

    # ---------------------------------------------------------
    # Основное поведение
    # ---------------------------------------------------------

    def accept_FA(self, word):
        """
        Интерпретирует входное слово по DFA-семантике и возвращает результат принятия.
        """
        state = self.initialState
        fired = []

        for symbol in word:
            key = self._lookup_key(state, symbol)
            if key is None:
                print(f"accept_FA: Error! no such transition: {state} {symbol}")
                return None
            fired.append(self._order.index(key))
            state = self.transitions[key]

        return self._is_final(state), fired

    def is_complete(self):
        """
        Проверяет, определена ли функция переходов для всех пар Q x Sigma.
        """
        return all(
            (state, symbol) in self.transitions
            for state in self._all_states()
            for symbol in self._all_inputs()
        )

    def complete(self, comptype="loop", reaction=0):
        """
        Дополняет partial DFA sink-состоянием и недостающими переходами.
        """
        if comptype not in {"loop", "DCS"}:
            print("Error! Specify completion type: loop or DCS")
            return None
        if comptype == "DCS" and not isinstance(reaction, int):
            print(f"reaction must be integer, not {type(reaction)}")
            return None

        states = self._all_states()
        inputs = self._all_inputs()
        if not states or not inputs:
            self.states = states
            self.inputs = inputs
            self._sync_declared_sizes()
            return reaction

        missing = [
            (state, symbol)
            for state in states
            for symbol in inputs
            if (state, symbol) not in self.transitions
        ]
        if not missing:
            self.states = states
            self.inputs = inputs
            self._sync_declared_sizes()
            return reaction

        sink = self._fresh_sink_state()
        self.states = set(states)
        self.inputs = set(inputs)
        self.states.add(sink)

        for state, symbol in missing:
            self._add_transition(state, symbol, sink, reaction if self.isFSM else None)
        for symbol in inputs:
            self._add_transition(sink, symbol, sink, reaction if self.isFSM else None)

        self._sync_declared_sizes()
        return reaction

    # ---------------------------------------------------------
    # Кодирование и структурные запросы
    # ---------------------------------------------------------

    def encode_states(self, is_abstraction=False, forced_transform=False):
        """
        Переименовывает состояния в целые числа, сохраняя язык автомата.
        """
        old_states = list(self._all_states())
        if self.initialState not in old_states:
            old_states.append(self.initialState)
        old_states.sort(key=lambda value: repr(value))
        mapping = {state: index for index, state in enumerate(old_states)}

        already_encoded = (
            not forced_transform
            and all(isinstance(s, int) for s in old_states)
            and set(old_states) == set(range(len(old_states)))
        )
        if already_encoded:
            return False, {}, {}

        old_transition_items = [(key, self.transitions[key]) for key in self._order]
        old_outputs = dict(self.outputs)

        self.transitions = {}
        self.outputs = {}
        self._order = []
        for (state, symbol), next_state in old_transition_items:
            output = old_outputs.get((state, symbol))
            self._add_transition(mapping[state], symbol, mapping[next_state], output)

        self.initialState = mapping[self.initialState]
        self.finalStates = {
            mapping[state]
            for state in old_states
            if self._state_was_final_before_encoding(state, old_states)
        }
        self.states = set(mapping.values())
        self.numberOfStates = len(self.states)

        reverse_mapping = {new: old for old, new in mapping.items()}
        abstraction_mapping = {new: old for new, old in reverse_mapping.items()} if is_abstraction else {}
        return True, reverse_mapping, abstraction_mapping

    def _state_was_final_before_encoding(self, state, old_states):
        """
        Проверяет, было ли состояние допускающим до кодирования.
        """
        if state in self.finalStates:
            return True
        try:
            if int(state) in self.finalStates:
                return True
        except (TypeError, ValueError):
            pass
        return str(state) in self.finalStates

    def get_states_list(self):
        """
        Возвращает список состояний автомата для совместимости с тестами.
        """
        if self._malformed_transitions:
            raise IndexError("Malformed transition has no next state")
        return list(self._all_states())

    def get_inputs_list(self):
        """
        Возвращает список входных символов автомата.
        """
        return list(self._all_inputs())

    def get_actions_list(self):
        """
        Возвращает входной алфавит в терминах legacy API.
        """
        if self._malformed_transitions:
            raise IndexError("Malformed transition has no input")
        return self.get_inputs_list()

    def get_outputs_list(self):
        """
        Возвращает множество выходов для FSM-совместимого режима.
        """
        return list(set(self.outputs.values()))

    def get_ns_out(self, state, inp):
        """
        Возвращает следующее состояние и выход для заданной пары состояние-вход.
        """
        key = self._lookup_key(state, inp)
        if key is None:
            raise Exception(f"get_ns_out error: no such (state, input) = ({state}, {inp})")
        return self.transitions[key], self.outputs.get(key, 0)

    def get_completely_undefined_states(self):
        """
        Находит состояния без исходящих переходов по всему алфавиту.
        """
        inputs = self._all_inputs()
        return [
            state
            for state in self._all_states()
            if inputs and all((state, symbol) not in self.transitions for symbol in inputs)
        ]

    def check_states_for_consistency(self):
        """
        Проверяет однородность типов состояний.
        """
        states = self.get_states_list()
        return len({type(state) for state in states}) <= 1

    def check_inputs_outputs_for_consistency(self):
        """
        Проверяет однородность типов входов и выходов.
        """
        values = self.get_actions_list() + self.get_outputs_list()
        return len({type(value) for value in values}) <= 1

    # ---------------------------------------------------------
    # Вспомогательные методы совместимости с FSM
    # ---------------------------------------------------------

    def move_seq_FSM(self, input_seq):
        """
        Обрабатывает входную последовательность в FSM-режиме и возвращает выходы и финальное состояние.
        """
        state = self.initialState
        output_seq = []
        for symbol in input_seq:
            key = self._lookup_key(state, symbol)
            if key is None:
                return None, None
            output_seq.append(self.outputs.get(key, 0))
            state = self.transitions[key]
        return output_seq, state

    def encode_inputs_outputs(self, forced_transform=False, dont_change_original=False):
        """
        Кодирует входы и выходы целыми числами для FSM-совместимости.
        """
        target = deepcopy(self) if dont_change_original else self

        inputs = list(target._all_inputs())
        outputs = list(set(target.outputs.values()))
        inputs.sort(key=lambda value: repr(value))
        outputs.sort(key=lambda value: repr(value))

        input_mapping = {value: index for index, value in enumerate(inputs)}
        output_mapping = {value: index for index, value in enumerate(outputs)}

        already_encoded = (
            not forced_transform
            and all(isinstance(i, int) for i in inputs)
            and all(isinstance(o, int) for o in outputs)
            and set(inputs) == set(range(len(inputs)))
            and set(outputs) == set(range(len(outputs)))
        )
        if already_encoded:
            return False, {}, {}

        old_items = [(key, target.transitions[key]) for key in target._order]
        old_outputs = dict(target.outputs)
        target.transitions = {}
        target.outputs = {}
        target._order = []
        target.inputs = set(input_mapping.values())
        target.numberOfInputs = len(target.inputs)
        target.numberOfOutputs = len(output_mapping)

        for (state, symbol), next_state in old_items:
            output = old_outputs.get((state, symbol))
            encoded_output = output_mapping[output] if output in output_mapping else output
            target._add_transition(state, input_mapping[symbol], next_state, encoded_output)

        if dont_change_original:
            return target, {v: k for k, v in input_mapping.items()}, {v: k for k, v in output_mapping.items()}
        return True, {v: k for k, v in input_mapping.items()}, {v: k for k, v in output_mapping.items()}

    def rename_inputs(self, mapping):
        """
        Переименовывает входные символы по заданному отображению.
        """
        assert len(mapping) == self.numberOfInputs
        new_items = []
        for key in self._order:
            state, symbol = key
            new_items.append((state, mapping.get(symbol, symbol), self.transitions[key], self.outputs.get(key)))
        self.transitionList = [
            item if item[3] is not None else item[:3]
            for item in new_items
        ]

    def sort_trans_table(self):
        """
        Сортирует порядок совместимого списка переходов без изменения семантики.
        """
        self._order.sort(key=lambda key: (repr(key[0]), repr(key[1])))

    def print_transition_table(self):
        """
        Печатает таблицу переходов в человекочитаемом виде.
        """
        for tr in self.transitionList:
            print(" ".join(str(part) for part in tr))

    # ---------------------------------------------------------
    # Совместимость с файловыми форматами
    # ---------------------------------------------------------

    @staticmethod
    def _parse_atom(value):
        """
        Преобразует строковый атом из файла в int, если это возможно.
        """
        try:
            return int(value)
        except ValueError:
            return value

    @staticmethod
    def read_FA(filename):
        """
        Читает автомат из простого FA-файла.
        """
        path = Path(filename)
        lines = path.read_text().splitlines()
        info = {}
        for line in lines[:4]:
            parts = line.strip().split()
            values = [FA_dict._parse_atom(part) for part in parts[1:]]
            info[parts[0]] = values[0] if len(values) == 1 else values

        fa = FA_dict()
        fa.isFSM = 0
        fa.numberOfStates = int(info.get("states_number", 0))
        fa.numberOfInputs = int(info.get("actions_number", 0))
        fa.initialState = info.get("start_state", 0)
        final_state = info.get("final_state", [])
        fa.finalStates = set(final_state if isinstance(final_state, list) else [final_state])
        fa.states.update(range(fa.numberOfStates))
        fa.inputs.update(range(fa.numberOfInputs))

        transitions = []
        for line in lines[4:]:
            parts = [FA_dict._parse_atom(part) for part in line.strip().split()]
            if parts:
                transitions.append(tuple(parts))
        fa.transitionList = transitions
        return fa

    @staticmethod
    def read_FSM(filename):
        """
        Читает FSM-файл и строит совместимый объект автомата.
        """
        path = Path(filename)
        lines = path.read_text().splitlines()
        fa = FA_dict()
        fa.isFSM = 1

        transitions = []
        observed_states = set()
        observed_inputs = set()
        observed_outputs = set()
        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue
            key = parts[0]
            if key == "s":
                fa.numberOfStates = int(parts[1])
                fa.states.update(range(fa.numberOfStates))
            elif key == "i":
                fa.numberOfInputs = int(parts[1])
                fa.inputs.update(range(fa.numberOfInputs))
            elif key == "o":
                fa.numberOfOutputs = int(parts[1])
            elif key == "n0":
                fa.initialState = FA_dict._parse_atom(parts[1])
            elif key[0].isdigit() or key[0] == "-":
                tr = tuple(FA_dict._parse_atom(part) for part in parts)
                transitions.append(tr)
                if len(tr) >= 3:
                    observed_states.update([tr[0], tr[2]])
                    observed_inputs.add(tr[1])
                if len(tr) >= 4:
                    observed_outputs.add(tr[3])

        fa.transitionList = transitions
        if (
            len(observed_inputs) != fa.numberOfInputs
            or len(observed_outputs) != fa.numberOfOutputs
            or len(observed_states) != fa.numberOfStates
        ):
            print("Error: fsm file is not consistent")
        return fa

    def write_FSM(self, filename):
        """
        Записывает автомат в FSM-совместимый текстовый формат.
        """
        path = Path(filename)
        lines = [
            "F 0",
            f"s {max(self.numberOfStates, len(self._all_states()))}",
            f"i {max(self.numberOfInputs, len(self._all_inputs()))}",
            f"o {max(self.numberOfOutputs, len(set(self.outputs.values())))}",
            f"n0 {self.initialState}",
            f"p {len(self.transitionList)}",
        ]
        lines.extend(" ".join(str(part) for part in tr) for tr in self.transitionList)
        path.write_text("\n".join(lines) + "\n")

    def write_FSM_init(self, filename, states_excluded=None):
        """
        Записывает FSM, исключая выбранные начальные состояния из переходов.
        """
        states_excluded = set(states_excluded or [])
        path = Path(filename)
        transitions = [tr for tr in self.transitionList if tr[0] not in states_excluded]
        lines = [
            "F 0",
            f"s {max(self.numberOfStates, len(self._all_states()))}",
            f"i {max(self.numberOfInputs, len(self._all_inputs()))}",
            f"o {max(self.numberOfOutputs, len(set(self.outputs.values())))}",
            f"n0 {self.initialState}",
            f"p {len(transitions)}",
        ]
        lines.extend(" ".join(str(part) for part in tr) for tr in transitions)
        path.write_text("\n".join(lines) + "\n")

    # ---------------------------------------------------------
    # Сравнение автоматов
    # ---------------------------------------------------------

    def __eq__(self, other):
        """
        Сравнивает два автомата по их формальным компонентам и совместимым полям.
        """
        if not isinstance(other, FA_dict):
            return False
        if (
            self._all_states() == other._all_states()
            and self._all_inputs() == other._all_inputs()
            and self.transitions == other.transitions
            and self.outputs == other.outputs
            and self.initialState == other.initialState
            and self.finalStates == other.finalStates
            and self.isFSM == other.isFSM
        ):
            return True
        print("difference")
        return False
