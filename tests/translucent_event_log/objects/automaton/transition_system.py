from pm4py.objects.transition_system import transition_system as ts
from datetime import timedelta

class TransitionSystem(ts.TransitionSystem):

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
