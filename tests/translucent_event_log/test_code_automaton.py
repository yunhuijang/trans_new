from tests.translucent_event_log.objects.tel.importer.xes.iterparse_tel import import_tel
import os
from tests.translucent_event_log.objects.tel.importer.xes.utils import log_to_tel
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.visualization.transition_system import factory as vis_factory
from tests.translucent_event_log.objects.tel import utils

input_file_path = os.path.join("input_data", "running-example.xes")
log = import_tel(input_file_path)
net, initial_marking, final_marking = alpha_miner.apply(log)

tel = log_to_tel(net, initial_marking, final_marking, log)

# for trace in tel:
#     for event in trace:
#         print(event['enabled'])
#         print(event['concept:name'])
#
auto = utils.discover_annotated_automaton(tel)
# for trans in auto.transitions:
#     print(trans)
#     print(trans.afreq)
#     print(trans.atsum)
#     print(trans.atavg)
#
# for states in auto.states:
#     print(states)
#     print(states.sfreq)
#     print(states.stsum)
#     print(states.stavg)

gviz = vis_factory.apply(auto)
vis_factory.view(gviz) #show automaton




