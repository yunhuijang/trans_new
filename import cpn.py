import os
from pm4py.objects.petri.importer import pnml as pnml_importer

net, initial_marking, final_marking = pnml_importer.import_net(os.path.join("tests","input_data","new net.pnml"))

from pm4py.visualization.petrinet import factory as pn_vis_factory

gviz = pn_vis_factory.apply(net, initial_marking, final_marking)
pn_vis_factory.view(gviz)


from pm4py.objects.petri import semantics

transitions = semantics.enabled_transitions(net, initial_marking)
print(transitions)
