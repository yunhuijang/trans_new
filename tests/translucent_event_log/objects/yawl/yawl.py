from pm4py.objects.petri import petrinet

class YawlNet(petrinet.PetriNet):
    class Place(petrinet.PetriNet.Place):

        def __init__(self, name, is_hidden=False, in_arcs=None, out_arcs=None):
            super().__init__(name, in_arcs, out_arcs)
            self.__is_hidden = False if is_hidden is None else is_hidden

        def __get_is_hidden(self):
                return self.__is_hidden

        is_hidden = property(__get_is_hidden)

    class Transition(petrinet.PetriNet.Transition):

        def __init__(self, name, is_hidden = False, join_type = None, split_type = None, label=None, in_arcs = None, out_arcs = None):
            super().__init__(name, label, in_arcs, out_arcs)
            self.__join_type = None if join_type is None else join_type
            self.__split_type = None if split_type is None else split_type
            self.__is_hidden = False if is_hidden is None else is_hidden

        def __get_join_type(self):
            return self.__join_type

        def __get_split_type(self):
            return self.__split_type

        def __get_is_hidden(self):
            return self.__is_hidden

        join_type = property(__get_join_type)
        split_type = property(__get_split_type)
        is_hidden = property(__get_is_hidden)