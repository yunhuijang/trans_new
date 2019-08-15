from pm4py.objects.transition_system import transition_system as ts
from datetime import timedelta
from tests.translucent_event_log_new.objects.automaton import defaults
from tests.translucent_event_log_new.algo.discover_automaton import utils
DEFAULT_TS_NAME = ""

class TransitionSystem(ts.TransitionSystem):

    def __init__(self, name=None, states=None, transitions=None):
        self.__name = "" if name is None else name
        self.__states = set() if states is None else states
        self.__transitions = set() if transitions is None else transitions
        self.state_matrix = {}
        self.trans_matrix = {}

    class State(ts.TransitionSystem.State):
        def __init__(self, name, id = None, incoming = None, outgoing = None, sfreq = None, stsum = None, stavg = None, data = None):
            super().__init__(name, incoming, outgoing, data)
            self.__id = 0 if id is None else id
            self.__sfreq = 0 if sfreq is None else sfreq
            self.__stsum = timedelta(microseconds=-1) if stsum is None else stsum
            self.__stavg = timedelta(microseconds=-1) if stavg is None else stavg

        def __get_sfreq(self):
            return self.__sfreq

        def __get_stsum(self):
            return self.__stsum

        def __get_stavg(self):
            return self.__stavg

        def __get_id(self):
            return self.__id

        def set_sfreq(self, sfreq):
            self.__sfreq = sfreq

        def set_stsum(self, stsum):
            self.__stsum = stsum

        def set_stavg(self, stavg):
            self.__stavg = stavg

        sfreq = property(__get_sfreq, set_sfreq)
        stsum = property(__get_stsum, set_stsum)
        stavg = property(__get_stavg, set_stavg)
        id = property(__get_id)

    class Transition(ts.TransitionSystem.Transition):

        def __init__(self, name, from_state, to_state, afreq = None, atsum = None, atavg = None, data=None):
            super().__init__(name, from_state, to_state, data)
            self.__afreq = 0 if afreq is None else afreq
            self.__atsum = timedelta(microseconds=-1) if atsum is None else atsum
            self.__atavg = timedelta(microseconds=-1) if atavg is None else atavg

        def __eq__(self, other):
            if self.name == other.name and self.from_state == other.from_state and self.to_state == other.to_state:
                return True
            else:
                return False

        def __hash__(self):
            return(hash(self.name))

        def __repr__(self):
            return str(self.name) + ": " + str(self.from_state) + " -> " + str(self.to_state)

        def __get_afreq(self):
                return self.__afreq

        def __get_atsum(self):
                return self.__atsum

        def __get_atavg(self):
                return self.__atavg

        def set_afreq(self, afreq):
            self.__afreq = afreq

        def set_atsum(self, atsum):
            self.__atsum = atsum

        def set_atavg(self, atavg):
            self.__atavg = atavg

        afreq = property(__get_afreq, set_afreq)
        atsum = property(__get_atsum, set_atsum)
        atavg = property(__get_atavg, set_atavg)

    def filter(self, afreq_thresh = defaults.DEFAULT_AFREQ_THRESH,
                  atsum_thresh = defaults.DEFAULT_ATSUM_THRESH, atavg_thresh = defaults.DEFAULT_ATAVG_THRESH,
                  sfreq_thresh = defaults.DEFAULT_SFREQ_THRESH, stsum_thresh = defaults.DEFAULT_STSUM_THRESH,
                  stavg_thresh = defaults.DEFAULT_STAVG_THRESH):
        self.state_matrix = None
        self.state_matrix = {}
        self.trans_matrix = None
        self.trans_matrix = {}

        states_set = set()
        trans_set = set()

        for state in self.states:
            s_name = str(state.name)
            self.state_matrix[s_name] = {}
            self.state_matrix[s_name]['sfreq'] = state.sfreq
            self.state_matrix[s_name]['stsum'] = state.stsum
            self.state_matrix[s_name]['stavg'] = state.stavg

        for s in self.state_matrix:
            condition1 = self.state_matrix[s]['sfreq'] >= sfreq_thresh
            condition2 = self.state_matrix[s]['stsum'] >= stsum_thresh
            condition3 = self.state_matrix[s]['stavg'] >= stavg_thresh
            condition = condition1 and condition2 and condition3
            if condition:
                for state in self.states:
                    if str(state.name) == s:
                        states_set.add(state)

        for trans in self.transitions:
            if trans.from_state in states_set and trans.to_state in states_set:
                self.trans_matrix[trans] = {}
                self.trans_matrix[trans]['afreq'] = trans.afreq
                self.trans_matrix[trans]['atsum'] = trans.atsum
                self.trans_matrix[trans]['atavg'] = trans.atavg

        for t in self.trans_matrix:
            t_condition2 = self.trans_matrix[t]['afreq'] >= afreq_thresh
            t_condition3 = self.trans_matrix[t]['atsum'] >= atsum_thresh
            t_condition4 = self.trans_matrix[t]['atavg'] >= atavg_thresh
            t_condition = t_condition2 and t_condition3 and t_condition4
            if t_condition:
                for trans in self.transitions:
                    if trans == t:
                        trans_set.add(trans)

        self.transitions = set()
        self.states = set()

        for s in states_set:
            self.states.add(s)
        for t in trans_set:
            self.transitions.add(t)
            utils.add_arc_from_to(t.name, t.from_state, t.to_state, self)







