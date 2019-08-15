
import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from tests.translucent_event_log_new.objects.tel.importer.xes import utils as xes_utils
from tests.translucent_event_log_new.objects.tel.importer.xes import iterparse_tel

from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.visualization.petrinet import factory as vis_factory
from tests.translucent_event_log.objects.tel import utils
from tests.translucent_event_log_new.algo.discover_petrinet import state_based_region as sb

input_file_path = os.path.join("input_data", "running-example.xes")
log = xes_importer.apply(input_file_path)
tel = iterparse_tel.import_tel(input_file_path)
xes_utils.set_enabled(tel)

for trace in tel:
    print(" ")
    for event in trace:
        print(event['enabled'])
        print(event['concept:name'])

auto = utils.discover_annotated_automaton(tel)

# nett, im, fm = sb.petri_net_synthesis(auto)
#
# gviz = vis_factory.apply(nett, im, fm)
# vis_factory.view(gviz)
#
# output_path = os.path.join("output_data", "receipt_tel.xes")
# xes_exporter.export_log(tel, output_path)









