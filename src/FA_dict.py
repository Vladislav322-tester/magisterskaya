"""
Альтернативная реализация конечного автомата (DFA_dict).

Отличия от FA_simple:
- переходы хранятся в dict
- более строгая семантика (нет "битых" переходов)
- нет зависимости от порядка transitionList
"""

class FA_dict:

    def __init__(self):
        self.states = set()
        self.inputs = set()
        self.transitions = {}  # (state, input) -> next_state
        self.initialState = None
        self.finalStates = set()
        self.isFSM = 0

    # ---------------------------------------------------------
    # INIT FROM DATA (адаптация под твои стратегии)
    # ---------------------------------------------------------

    @classmethod
    def from_data(cls, data):
        fa = cls()

        fa.states = set(data.get("states", []))
        fa.inputs = set(data.get("inputs", []))
        fa.initialState = data.get("initial_state")
        fa.finalStates = set(data.get("final_states", []))
        fa.isFSM = 1 if data.get("is_fsm", False) else 0

        for t in data.get("transitions", []):
            if len(t) >= 3:
                s, i, ns = t[:3]
                fa.transitions[(s, i)] = ns

        return fa

    # ---------------------------------------------------------
    # CORE METHODS
    # ---------------------------------------------------------

    def accept_FA(self, word):
        state = self.initialState

        for symbol in word:
            key = (state, symbol)

            if key not in self.transitions:
                return False

            state = self.transitions[key]

        return state in self.finalStates

    # ---------------------------------------------------------
    # STATES / INPUTS
    # ---------------------------------------------------------

    def get_states_list(self):
        return list(self.states)

    def get_inputs_list(self):
        return list(self.inputs)

    def get_actions_list(self):
        return self.get_inputs_list()

    @property
    def transitionList(self):
        return [(s, i, ns) for (s, i), ns in self.transitions.items()]

    @transitionList.setter
    def transitionList(self, transitions):
        self.transitions = {}
        self.states = set()
        self.inputs = set()
        for t in transitions:
            if len(t) >= 3:
                s, i, ns = t[:3]
                self.states.update([s, ns])
                self.inputs.add(i)
                self.transitions[(s, i)] = ns

    # ---------------------------------------------------------
    # ENCODE STATES (аналог твоего метода)
    # ---------------------------------------------------------

    def encode_states(self, forced_transform=False):
        mapping = {s: i for i, s in enumerate(sorted(self.states))}

        new_transitions = {}
        for (s, i), ns in self.transitions.items():
            new_transitions[(mapping[s], i)] = mapping[ns]

        self.transitions = new_transitions
        self.states = set(mapping.values())

        if self.initialState in mapping:
            self.initialState = mapping[self.initialState]

        self.finalStates = {mapping[s] for s in self.finalStates if s in mapping}

    # ---------------------------------------------------------
    # COMPLETENESS
    # ---------------------------------------------------------

    def is_complete(self):
        for s in self.states:
            for i in self.inputs:
                if (s, i) not in self.transitions:
                    return False
        return True

    def complete(self):
        if not self.states:
            return

        sink = max(self.states) + 1 if self.states else 0

        for s in list(self.states):
            for i in self.inputs:
                if (s, i) not in self.transitions:
                    self.transitions[(s, i)] = sink

        # добавляем sink transitions
        if self.inputs:
            for i in self.inputs:
                self.transitions[(sink, i)] = sink

        self.states.add(sink)

    # ---------------------------------------------------------
    # EQUALITY
    # ---------------------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, FA_dict):
            return False

        return (
            self.states == other.states and
            self.inputs == other.inputs and
            self.transitions == other.transitions and
            self.initialState == other.initialState and
            self.finalStates == other.finalStates
        )
