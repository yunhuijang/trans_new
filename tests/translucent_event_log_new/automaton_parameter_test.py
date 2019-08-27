from tests.translucent_event_log.objects.tel.importer.xes.iterparse_tel import import_tel
import os
from tests.translucent_event_log_new.objects.tel.importer.xes.utils import log_to_tel
from pm4py.algo.discovery.alpha import factory as alpha_miner
from tests.translucent_event_log_new.objects.tel.utils import tel_set_enabled
from pm4py.visualization.transition_system import factory as vis_factory
from pm4py.visualization.petrinet import factory as petri_factory
from tests.translucent_event_log_new.algo.discover_automaton import utils
from datetime import timedelta
from tests.translucent_event_log_new.algo.discover_petrinet import state_based_region as sb

input_file_path = os.path.join("input_data", "running-example_tel.xes")
log = import_tel(input_file_path)
tel = tel_set_enabled(log)

auto = utils.discover_annotated_automaton(tel)
gviz = vis_factory.apply(auto)
vis_factory.view(gviz) #show automaton


auto = utils.discover_annotated_automaton(tel, parameters={'sfreq_thresh' : 2, 'afreq_thresh' : 3})

gviz = vis_factory.apply(auto)
vis_factory.view(gviz) #show automaton

nett, im, fm = sb.petri_net_synthesis(auto)
#
gviz = petri_factory.apply(nett, im, fm)
petri_factory.view(gviz)