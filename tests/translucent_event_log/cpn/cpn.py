from pm4py.objects.petri.petrinet import Marking
from pm4py.objects.petri.petrinet import PetriNet


class cpn(PetriNet):

    class Place(PetriNet.Place):

        def __init__(self, name, type, in_arcs = None, out_arcs = None):
            self.__name = name
            self.__type = type
            self.__in_arcs = set() if in_arcs is None else in_arcs
            self.__out_arcs = set() if out_arcs is None else out_arcs

        def __get_type(self):
            return self.__type

        def __repr__(self):
            return str(self.name) + ":" + str(self.type)

        type = property(__get_type)

    class Transition(PetriNet.Transition):
        def __init__(self, name, label=None, in_arcs=None, out_arcs=None, guard = None):
            self.__name = name
            self.__label = None if label is None else label
            self.__in_arcs = set() if in_arcs is None else in_arcs
            self.__out_arcs = set() if out_arcs is None else out_arcs
            self.__guard = None if guard is None else guard

        def __get_guard(self):
            return self.__guard

        guard = property(__get_guard)

    class Arc(PetriNet.Arc):
        def __init__(self, source, target, weight=1, expression=None):
            if type(source) is type(target):
                raise Exception('Petri nets are bipartite graphs!')
            self.__source = source
            self.__target = target
            self.__weight = weight
            self.__expression = expression

        def __get_expression(self):
            return self.__expression

        def __repr__(self):
            if type(self.source) is PetriNet.Transition:
                if self.source.label:
                    return "(t)"+str(self.source.label) + "->" + "(p)"+str(self.target.name) + str(self.expression.name)
                else:
                    return "(t)"+str(self.source.name) + "->" + "(p)"+str(self.target.name) + str(self.expression.name)
            if type(self.target) is PetriNet.Transition:
                if self.target.label:
                    return "(p)"+str(self.source.name) + "->" + "(t)"+str(self.target.label) + str(self.expression.name)
                else:
                    return "(p)"+str(self.source.name) + "->" + "(t)"+str(self.target.name) + str(self.expression.name)

        expression = property(__get_expression)




