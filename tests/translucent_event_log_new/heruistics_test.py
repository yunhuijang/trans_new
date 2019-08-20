
import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from tests.translucent_event_log_new.objects.tel.importer.xes import utils as xes_utils
from tests.translucent_event_log_new.objects.tel.importer.xes import iterparse_tel

from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.visualization.petrinet import factory as vis_factory
from pm4py.visualization.transition_system import factory as trans_fact
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


output_path = os.path.join("input_data", "running-example_tel.xes")
xes_exporter.export_log(tel, output_path)









