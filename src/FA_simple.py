from __future__ import annotations  # для #uyB3sWj2s9J

import copy
import re
from collections.abc import Sequence
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Set,
    Tuple,
    TypeVar,
)

if TYPE_CHECKING:
    from .FA import FA
    from .MYEFA import MYEFA


class FA_simple(object):
    """
    Класс для общих операций с автоматами (полуавтоматами).

    """

    def __init__(self) -> None:
        self.initialState: str | int = 0
        self.finalStates: set[str | int]
        self.numberOfStates: int = 0
        self.numberOfInputs: int = 0
        self.numberOfOutputs: int = 0
        self.transitionList: Any = []  # list[Sequence[int | str]] = []
        self.isFSM: int = 0

    def __eq__(self, other):
        if len(self.transitionList) != len(other.transitionList):
            return False
        for i in range(len(self.transitionList)):
            if list(self.transitionList[i]) != list(other.transitionList[i]):
                print(f"difference in {i} transition")
                print(self.transitionList[i])
                print(other.transitionList[i])
                return False
        return True

    ###################################################
    # ВВОД-ВЫВОД
    def print_transition_table(self):
        """Печатает список переходов автомата self.
        Args:
                self(FA_simple).
        Returns:
                None

        """
        for tr in self.transitionList:
            for el in tr:
                print(el, end=" ")
            print()
        print()

    @staticmethod
    def from_efa(efa: "MYEFA") -> "FA_simple":
        """Преобразует расширенный полуавтомат (для расширенного _автомата_ не проверялась) в классический полуавтомат.
                просто отбрасывая предикаты и апдейт функции
                TODO заполнить поля numberOfInputs, numberOfStates,....
                TODO проверить для автомата MYEFA
        Args:
                efa(MYEFA). (только полуавтомат?)

        Returns:
                FA_simple. (только полуавтомат?)

        """
        res = FA_simple()
        for tr in efa.transitionList:
            res.transitionList.append((tr.state1, tr.input, tr.state2))
        res.initialState = copy.copy(efa.initialState)
        res.finalStates = copy.deepcopy(efa.finalStates)
        return res

    @staticmethod
    def from_FA(fa: "FA") -> "FA_simple":
        """Преобразует полуавтомат предикатной абстракции в обычный полуавтомат.
        Args:
                fa(FA): автомат (ожидаем, что это - предкатная абстракция)
                        TODO: Если fa - это не предикатная абстракция, то зачем вообще нужен класс FA?

        Returns:
                FA_simple.

        """
        res = FA_simple()
        res.initialState = fa.initialState
        res.transitionList = fa.transitionList
        res.isFSM = fa.isFSM
        res.numberOfStates = len(res.get_states_list())
        res.numberOfInputs = len(res.get_actions_list())

        if res.isFSM == 1:
            res.numberOfOutputs = fa.numberOfOutputs
        else:
            res.finalStates = fa.finalStates
        return res

    def write_FSM(self, filename):
        """Выводит описание автомата в текстовый формат "fsm".

        Args:
                self(FA_simple).

                filename (str): Имя файла, куда будет записан автомат.
        """
        from operator import itemgetter

        states = sorted(self.get_states_list())
        actions = sorted(self.get_actions_list())
        outputs = sorted(self.get_outputs_list())

        fsmtext = f"F 0\ns {len(states)}\ni {len(actions)}\no {len(outputs)}\nn0 {self.initialState}\np {len(self.transitionList)}\n"
        # заменим сложные имена состояний на их индексы в массиве состояний
        # fsmtext += f"start_state {states.index(self.initialState)}\n"
        # c = " ".join(sorted([str(states.index(x)) for x in self.finalStates]))
        # fsmtext += f"final_state {c}\n"
        sortedtranslist = sorted(
            [x for x in self.transitionList], key=itemgetter(0, 1, 2)
        )
        for tr in sortedtranslist:
            fsmtext += f"{tr[0]} {tr[1]} {tr[2]} {tr[3]}\n"

        with open(filename, "w") as file:
            file.write(fsmtext)

    def write_FSM_init(self, filename, states_excluded=[]):
        """Вывод в файл слабо инициального (неинициального) автомата в формате "fsm".
                т.е. в преамбуле в формате "fsm" в строке n0 пречисляются несколько состояний

        TODO объединить с функцией write_FSM

        Args:
                states_excluded(list):  список состояний, которые не добавляются в множество начальных.

        """
        from operator import itemgetter

        states = sorted(self.get_states_list())
        actions = sorted(self.get_actions_list())
        outputs = sorted(self.get_outputs_list())

        states_list_len = len(states)

        states_excluded = [str(x) for x in states_excluded]

        init_states = [
            str(x) for x in range(states_list_len) if str(x) not in states_excluded
        ]
        fsmtext = f"F 0\ns {len(states)}\ni {len(actions)}\no {len(outputs)}\nn0 {' '.join(x for x in init_states)}\np {len(self.transitionList)}\n"

        # заменим сложные имена состояний на их индексы в массиве состояний
        # fsmtext += f"start_state {states.index(self.initialState)}\n"
        # c = " ".join(sorted([str(states.index(x)) for x in self.finalStates]))
        # fsmtext += f"final_state {c}\n"
        sortedtranslist = sorted(
            [x for x in self.transitionList], key=itemgetter(0, 1, 2)
        )
        for tr in sortedtranslist:
            fsmtext += f"{tr[0]} {tr[1]} {tr[2]} {tr[3]}\n"

        with open(filename, "w") as file:
            file.write(fsmtext)

    @staticmethod
    def read_FSM(filename):
        """Считывает автомат из файла в формате "fsm".
        Также, проверяет корректность преамбулы.

        # TODO Добавить вызов consistency_check

        Args:
                filename(str): имя файла с автоматом в формате "fsm".

        Returns:
                FA_simple

        """
        fsm = FA_simple()
        fsm.isFSM = 1
        fsm_file = open(filename, "r")
        fsm_list = list(fsm_file)
        fsm_file.close()
        info: dict[str, int] = dict()
        for line in fsm_list[:6]:
            splitted = line.strip().split(" ")
            info[splitted[0]] = int(splitted[1]) if len(splitted) == 2 else [int(x) for x in splitted[1:]]  # type: ignore

        fsm.numberOfStates = info["s"]
        fsm.numberOfInputs = info["i"]
        fsm.numberOfOutputs = info["o"]
        fsm.initialState = info["n0"]

        for line in fsm_list[6:]:
            elems = [s.strip() for s in line.split(" ")]
            fsm.transitionList.append(elems)

        inp_num_check = len(fsm.get_actions_list())  # inputs
        out_num_check = len(fsm.get_outputs_list())
        sts_num_check = len(fsm.get_states_list())

        if (
            inp_num_check != fsm.numberOfInputs
            or out_num_check != fsm.numberOfOutputs
            or sts_num_check != fsm.numberOfStates
        ):
            print("Error: fsm file is not consistent")

        return fsm

    @staticmethod
    def read_FA(filename):
        """Считывает полуавтомат из файла в формате "fa".
        TODO: проверка корректности преамбулы.

        Args:
                filename(str): имя файла с автоматом в формате "fsm".

        Returns:
                FA_simple.

        """
        fsm = FA_simple()
        fsm.isFSM = 0
        fsm_file = open(filename, "r")
        fsm_list = list(fsm_file)
        fsm_file.close()
        info: dict[str, Any] = dict()  #
        for line in fsm_list[:4]:
            splitted = line.strip().split(" ")
            info[splitted[0]] = (
                int(splitted[1])
                if len(splitted) == 2
                else [int(x) for x in splitted[1:]]
            )

        fsm.numberOfStates = info["states_number"]
        fsm.numberOfInputs = info["actions_number"]
        fsm.initialState = info["start_state"]
        if fsm.isFSM == 0:
            if type(info["final_state"]) == list:
                fsm.finalStates = set(info["final_state"])
            else:
                fsm.finalStates = set([info["final_state"]])
        else:
            fsm.finalStates = set()

        for line in fsm_list[4:]:
            elems = [s.strip() for s in line.split(" ")]
            fsm.transitionList.append(elems)

        return fsm

    #######################################
    # GET INFO

    def get_ns_out(self, state: int, inp: int) -> tuple[int, int]:
        """Возвращает (nnext_state, reaction) для автомата в состоянии state при подаче inp"""
        for tr in self.transitionList:
            if str(tr[0]) == str(state) and str(tr[1]) == str(
                inp
            ):  # TODO убрать приведение к str
                return (tr[2], tr[3])
        raise Exception(
            f"get_ns_out error: no such (state, input) = ({state}, {inp}) in the FSM"
        )

    def get_states_list(self) -> list[int | str]:
        """Возвращает список всех состояний автомата на основе списка переходов.
        Args:
                self (FA_simple).

        Returns:
                list: все состояни автомата из списка переходов.
        """
        states = set()
        for tr in self.transitionList:
            states.add(tr[0])
            states.add(tr[2])
        return list(states)

    def get_actions_list(self) -> list[int | str]:
        """Возвращает список всех входных символов (действий) (полу)автомата на основе списка переходов.
        Args:
                self (FA_simple).

        Returns:
                list: все входные символы (действия) (полу)автомата из списка переходов.
        """
        actions = set()
        for tr in self.transitionList:
            actions.add(tr[1])
        return list(actions)

    def get_outputs_list(self) -> list[int | str]:
        """Возвращает список всех выходных символов автомата на основе списка переходов.
        Args:
                self (FA_simple).

        Returns:
                list: все выходные символы автомата из списка переходов.
        """
        outputs = set()
        for tr in self.transitionList:
            outputs.add(tr[3])
        return list(outputs)

    #######################################
    # CHECKING

    def check_states_for_consistency(self) -> bool:
        """В FA_simple принято следующее: состояния, входы, выходы, записанные на переходах могут быть числами или строками

        Args:
                self
        Returns:
                bool: True - если все состояния имеют одинаковый тип; Иначе - False.
        """
        type_ = type(self.transitionList[0][0])
        for tr in self.transitionList:
            for i in [0, 2]:
                if type(tr[i]) != type_:
                    return False
        return True

    def check_inputs_outputs_for_consistency(self) -> bool:
        """В FA_simple принято следующее: состояния, входы, выходы, записанные на переходах могут быть числами или строками

        Args:
                self
        Returns:
                bool: True - если все входы и выходы на всех переходах имеют одинаковый тип; False иначе.
                0 - иначе
        """
        type_ = type(self.transitionList[0][1])
        for tr in self.transitionList:
            for i in [1, 3]:
                if type(tr[i]) != type_:
                    return False
        return True

    def is_complete(self):
        """Проверяет является ли автомат полостью определенным.
        Args:
                self (FA_simple).

        Returns:
                bool:
                        True - автомат полностью определенный
                        False - иначе.
        """
        if len(self.transitionList) != self.numberOfStates * self.numberOfInputs:
            # print (f"params: {self.numberOfStates} {self.numberOfInputs} --- trnum {len(self.transitionList)}")
            return False

        for s in self.get_states_list():
            for i in self.get_actions_list():
                for tr in self.transitionList:
                    if tr[0] == s and tr[1] == i:
                        break
                else:
                    # print (f"cant find trans for : {s=} {i=}")
                    return False
        return True

    def get_completely_undefined_states(self):
        """Выдает список состояний, в которых не определено ни одного входного символа.
        Args:
                self(FA_simple).

        Returns:
                list: список состояний
        stdout: no

        """
        undef_states = []
        for state in self.get_states_list():
            for tr in self.transitionList:
                if tr[0] == state:
                    break
            else:
                undef_states.append(state)
        return undef_states

    #######################################

    # TRANSFORMATIONS
    def rename_inputs(self, from_to_dict: dict[int | str, int | str]) -> None:
        """Переименовывает входы автомата self в соответствии со словарем from_to_dict
        Args:
                self (FA_simple).
                from_to_dict (dict): соответствие старых и новых символов.
        Returns:
                None

        """
        assert (
            len(set(from_to_dict.keys())) == self.numberOfInputs
        ), "Cannot rename inputs"

        new_tr_list: list[Sequence[int | str]] = []
        for transition in self.transitionList:
            new_tr_list.append(
                (
                    transition[0],
                    from_to_dict[transition[1]],
                    transition[2],
                    transition[3],
                )
            )

        self.transitionList = new_tr_list

    def sort_trans_table(self) -> None:
        """Сортирует список переходов по состояниию и входному символу."""
        from operator import itemgetter

        # print ("FSM transitions has been sorted")
        self.transitionList.sort(key=itemgetter(0, 1))

    def encode_states(
        self, is_abstraction: bool = False, forced_transform: bool = False
    ) -> tuple[bool, dict[int, str], dict[int, int]]:
        """Кодирует состояния целыми числами.
        Cостояния кодируются целыми числами от 0 до len(self.numberOfStates) в порядке их появления на переходах.

        Args:
                forced_transform(bool):
                        True: Независимо от того, являются ли состояния уже числами (хоть и в виде str),
                                перекодирует их в тип int (в порядке появления в списке переходов). Если новая кодировка отличается от старой, выводит сообщение:
                                "States encoding has been changed"
                        False: оставляет исходные состояния, применяя преобразование int(str_state) если можно, если нет - кодирует такие состояния
                                целыми числами по порядку от 0 в порядке появления на переходах

                is_abstraction(bool):
                        True: Работаем с автоматом self как с абстракцией (напр, l-эквивалент или др).
                                Для автомата-абcтракции на основе кодировки состояний (конфигураций EFSM) в абстракции : конфигурация -> целое_число (порядковый номер)
                                        формируется словарь abs_IntState_to_EFFSM_IntState с этими парами new_state -> EFSM_state, где
                                new_state - целое число-код конфигурации
                                EFSM_state - целое число-код состояния EFSM (в той кодировке, которая была в файле ".efsm") в этой конфигурации
                        False: Работаем как с автомаом с обычными состояниями.
                                возвращается только словарь abs_Intstate_to_abs_State, с парами new_state(int) -> old_state(str)

        Returns:
                Tuple:
                        bool: True - если перекодирование было (иначе False), тогда возвращается один (иногда два) словарь:
                        dict[int, str]: abs_Intstate_to_abs_State словарь: new_state(int) -> old_state(str)(конфигурация EFSM в случае абстракции (l-экв))
                        dict[int, str]: abs_IntState_to_EFFSM_IntState (опционально) словарь: new_state(int) -> EFSM_state(int)(это состояние выделяется из old_state(str))

        """

        # проверяем все состояния, чтобы они были числами
        is_ok = 1
        if (
            type(self.transitionList[0][0]) != int
            or not self.check_states_for_consistency()
        ):
            is_ok = 0
        else:
            return False, dict(), dict()
            # может, вместо пустого словаря возвращать словарь (отображение типа x->x)?

        # if len(self.transitionList) != self.numberOfStates * self.numberOfInputs:
        # print ("ERROR! FSM is partial")

        state_encoding_has_been_changed = 0

        if self.isFSM:
            self.transitionList = [
                (str(x[0]), str(x[1]), str(x[2]), str(x[3]))
                for x in self.transitionList
            ]
        else:
            self.transitionList = [
                (str(x[0]), str(x[1]), str(x[2])) for x in self.transitionList
            ]
        self.initialState = str(self.initialState)

        abs_Intstate_to_abs_State = {}  # integer_coded_name -> old_str_name
        abs_Intstate_to_abs_State_reversed = {}  # old_str_name -> integer_coded_name
        state_number_counter = 0

        if self.initialState.isdigit():
            abs_Intstate_to_abs_State[int(self.initialState)] = self.initialState
            abs_Intstate_to_abs_State_reversed[self.initialState] = int(
                self.initialState
            )
        else:
            abs_Intstate_to_abs_State[0] = self.initialState
            abs_Intstate_to_abs_State_reversed[self.initialState] = 0
            state_number_counter += 1

        for tr in self.transitionList:
            for sst in [tr[0], tr[2]]:
                if sst not in abs_Intstate_to_abs_State_reversed:
                    if type(sst) != int and sst.isdigit() and not forced_transform:
                        state_number = int(sst)
                    else:
                        state_number = state_number_counter
                        state_number_counter += 1
                        state_encoding_has_been_changed = 1
                    abs_Intstate_to_abs_State[state_number] = sst
                    abs_Intstate_to_abs_State_reversed[sst] = state_number

        if self.isFSM == 1:
            self.transitionList = [
                (
                    abs_Intstate_to_abs_State_reversed[x[0]],
                    x[1],
                    abs_Intstate_to_abs_State_reversed[x[2]],
                    x[3],
                )
                for x in self.transitionList
            ]
        else:
            self.transitionList = [
                (
                    abs_Intstate_to_abs_State_reversed[x[0]],
                    x[1],
                    abs_Intstate_to_abs_State_reversed[x[2]],
                )
                for x in self.transitionList
            ]
        self.numberOfInputs = len(set([x[1] for x in self.transitionList]))

        self.initialState = abs_Intstate_to_abs_State_reversed[self.initialState]

        if is_abstraction == 1:
            abs_IntState_to_EFFSM_IntState = dict()
            pattern = re.compile(r"\('(\d+)'")

            for k, v in abs_Intstate_to_abs_State.items():
                abs_IntState_to_EFFSM_IntState[k] = int(pattern.match(v).groups()[0])  # type: ignore
        else:
            abs_IntState_to_EFFSM_IntState = None

        if state_encoding_has_been_changed == 1:
            print("States encoding has been changed")

        return bool(state_encoding_has_been_changed), abs_Intstate_to_abs_State, abs_IntState_to_EFFSM_IntState  # type: ignore

    def encode_inputs_outputs(
        self, forced_transform: bool = False, dont_change_original: bool = False
    ) -> tuple[bool | "FA_simple", dict, dict]:  # uyB3sWj2s9J
        """Кодирует действия в списке переходов целыми числами.
        todo описать и доработать как в encode_states

        Args:
                forced_transform (bool): Аналогично методу encode_states.

                dont_change_original (bool):
                        True: Будет создана копия автомата и все изменения применяются к ней, и она возвращается. self не изменяется.

        Returns:
                tuple:
                        bool:
                                True - если перекодирование было, иначе - False.
                        dict[int, int | str]: new_input2abs_input: new_input(int) -> abs_input(int, possibly str)
                                new_input - новый int код входа, такой, чтобы все входы были по порядку [0,1,2...]
                                abs_input - старый вход абстракции (l-эквивалента)

                        dict[int, int | str]: new_output2abs_output - аналогично new_input2abs_input
        """
        from copy import deepcopy

        is_ok = 1
        # чтобы не делать лишнюю работу
        for i in range(len(self.transitionList)):
            if (
                type(self.transitionList[i][1]) != int
                or type(self.transitionList[i][3]) != int
            ):
                is_ok = 0
                break
        if (
            is_ok == 1
            and max(self.get_actions_list()) == self.numberOfInputs - 1
            and max(self.get_outputs_list()) == self.numberOfOutputs - 1
        ):
            return (False, dict(), dict())

        fsm = self
        if dont_change_original == 1:
            fsm = deepcopy(self)

        new_input2abs_input = dict()
        new_input2abs_input_reversed = dict()
        new_output2abs_output = dict()
        new_output2abs_output_reversed = dict()
        no_transformation = 1

        input_number_counter = 0
        output_number_counter = 0
        for tr in fsm.transitionList:
            if tr[1] not in new_input2abs_input_reversed:  # пока нельзя int(tr[1])
                if type(tr[1]) != int and tr[1].isdigit() and not forced_transform:
                    input_number = int(tr[1])
                else:
                    input_number = input_number_counter
                    input_number_counter += 1
                    no_transformation = 0
                new_input2abs_input[input_number] = tr[1]
                new_input2abs_input_reversed[tr[1]] = input_number
            if tr[3] not in new_output2abs_output_reversed:  # пока нельзя int(tr[3])
                if type(tr[3]) != int and tr[3].isdigit() and not forced_transform:
                    output_number = int(tr[3])
                else:
                    output_number = output_number_counter
                    output_number_counter += 1
                    no_transformation = 0
                new_output2abs_output[output_number] = tr[3]
                new_output2abs_output_reversed[tr[3]] = output_number

        if fsm.isFSM == 1:
            fsm.transitionList = [
                (
                    x[0],
                    new_input2abs_input_reversed[x[1]],
                    x[2],
                    new_output2abs_output_reversed[x[3]],
                )
                for x in fsm.transitionList
            ]
        else:
            fsm.transitionList = [
                (x[0], new_input2abs_input_reversed[x[1]], x[2])
                for x in fsm.transitionList
            ]

        if no_transformation == 1:
            return False, dict(), dict()
        else:
            if dont_change_original == 1:
                return fsm, new_input2abs_input, new_output2abs_output
            return (True, new_input2abs_input, new_output2abs_output)

    def complete(self, comptype="loop", reaction=0):
        """Доопределяет частичный автомат либо петлей либо с помощью Don't Care State
        Необходимо чтобы состояния, входы и выходы были закодированы целыми числами
        Для этого есть методы encode_states, encode_inputs_outputs

        Args:
                comptype (str). Одно из: 'loop' | 'DCS'. TODO заменить на enum
                        'loop' - доопределение петлей с добавляемой в выходной алфавит реакцией
                                Код новой реакции равен n+1, где n - максимальный код реакции в автомате до доопределения.
                        'DCS' - доопределение с помощью перехода в don't care state (DCS) с реакцией reaction

                reaction (int): реакция для доопределенных переходов в don't care state. Не используется если comptype == 'loop'
                        ! если автомат - это КА-абстракция расширенного автомата, то в качестве reaction надо указать ту
                        реакцию, которая использовалась в методе MYEFA.complete_loop().

        Returns:
                reaction (int) - реакция, фактически использованная для доопределения

                 // DCS нет смысла возвращать, т.к. он равен self.numberOfStates - 1
        """
        if comptype == "DCS":
            if type(reaction) != int:
                print(f"reaction must be integer, not {type(reaction)}")
                return
            DC_state = self.numberOfStates
        elif comptype == "loop":
            # reaction = len(self.get_outputs_list())
            pass
        else:
            print(f"Error! Specify completion type: loop or DCS")
            return

        for s in range(0, self.numberOfStates):
            for i in range(0, self.numberOfInputs):
                for tr in self.transitionList:
                    if tr[0] == s and tr[1] == i:
                        break
                else:
                    if comptype == "DCS":
                        self.transitionList.append((s, i, DC_state, reaction))
                    else:
                        self.transitionList.append((s, i, s, reaction))

        if comptype == "DCS":
            self.numberOfStates += 1
            for i in range(0, self.numberOfInputs):
                self.transitionList.append((DC_state, i, DC_state, reaction))

        self.numberOfOutputs += 1

        return reaction

    #######################################
    # SIMULATION

    def move_seq_FSM(self, input_seq):
        """Принимает входную последовательность и симулирует автомат.

        Args:
                self (FA_simple).

                input_seq (list[int, str]): последовательность входных символов автомата.

        Returns:
                list[int, str]: выдает последовательность реакций.

        """
        reaction_seq = []
        current_state = str(self.initialState)
        for inp in input_seq:
            for tr in self.transitionList:
                if str(tr[0]) == str(current_state) and str(tr[1]) == str(inp):
                    reaction_seq.append(tr[3])
                    current_state = tr[2]
                    break
            else:
                # print(f"move_seq_FSM: Error! no such transition: s {current_state} i {inp}")
                return None, None
        return reaction_seq, current_state

    def accept_FA(self, input_seq):
        """Проверяет принимает ли полуавтомат входную последовательность.
        принимает последовательность, выдает True если ПА принимает ее, иначе - False
        Args:
                input_seq (list): вх посл-ть

        Returns:
                Tuple[bool, set]
                        bool: True - если полуавтомат принимает
                        set : список номеров переходов, покрытых поданной последовательностью

        """
        fired_trans = set()
        current_state = str(self.initialState)
        for inp in input_seq:
            for i in range(len(self.transitionList)):
                if str(self.transitionList[i][0]) == str(current_state) and str(
                    self.transitionList[i][1]
                ) == str(inp):
                    current_state = self.transitionList[i][2]
                    fired_trans.add(i)
                    break
            else:
                print(f"accept_FA: Error! no such transition: {current_state} {inp}")
                return None
        if int(current_state) in self.finalStates:
            return True, fired_trans
        else:
            return False, fired_trans

    #######################################
    # OTHER
